from flask import Blueprint, render_template, request, session, redirect
from database import db
from models import MultiplayerSession
import game_engine
from utils.helpers import (
    cleanup_stale_mp_sessions, generate_room_code, get_card_count,
    get_card, deal_mp_decks
)

mp_bp = Blueprint('multiplayer', __name__)

#Multiplayer Features
@mp_bp.route("/mp/handle_create", methods=["POST"])
def handle_create_room():
    """Generates a room code, sets current user as host, and sends them to the lobby."""
    user_id = session.get('user_id')
    if not user_id:
        return render_template("login.html", error="Please log in to create a room!")
    cleanup_stale_mp_sessions()
    deck_theme = request.form.get("deck_theme", "ipl")
    deck_size = int(request.form.get("deck_size", 5))
    room_code = generate_room_code()

    new_session = MultiplayerSession(
        room_code=room_code,
        host_id=user_id,
        deck_theme=deck_theme,
        deck_size=deck_size,
        status="waiting",
        turn=1
    )

    db.session.add(new_session)
    db.session.commit()

    return redirect(f"/mp/lobby/{room_code}")

@mp_bp.route("/mp/create")
def create_room_page():
    user_id = session.get('user_id')
    if not user_id:
        return render_template("login.html", error="Please log in to create a room!")
    
    return render_template("create_room_theme.html")

@mp_bp.route("/mp/create/size")
def create_room_size():
    user_id = session.get('user_id')
    if not user_id:
        return render_template("login.html", error="Please log in to create a room!")

    deck_theme = request.args.get("deck_theme", "ipl")
    
    # Calculate exact max cards for this theme (each player gets up to half the pool)
    max_cards = get_card_count(deck_theme)

    return render_template("create_room_size.html", deck_theme=deck_theme, max_cards=max_cards)

@mp_bp.route("/mp/handle_join", methods=["POST"])
def handle_join_room():
    """Validates room code, joins guest, deals IPL decks, and starts the match."""
    user_id = session.get('user_id')
    if not user_id:
        return render_template("login.html", error="Please log in to join a room!")

    room_code = request.form.get("room_code", "").strip().upper()
    
    if not room_code:
        return render_template("home.html", user={'username': session.get('guest_id', 'Guest'), 'is_guest': False}, error="Please enter a room code!")

    game_room = MultiplayerSession.query.filter_by(room_code=room_code, status="waiting").first()

    if not game_room:
        return render_template("home.html", user={'username': session.get('guest_id', 'Guest'), 'is_guest': False}, error="Invalid or expired Room Code!")

    if game_room.host_id == user_id:
        # If host re-enters their own code, send them back to their lobby
        return redirect(f"/mp/lobby/{room_code}")

    # Attach Guest
    game_room.guest_id = user_id

    # Deal Decks from choosen deck pool
    host_cards, guest_cards = deal_mp_decks(theme=game_room.deck_theme, deck_size=game_room.deck_size)
    game_room.host_deck = host_cards
    game_room.guest_deck = guest_cards
    game_room.status = "active"

    db.session.commit()

    # Guest enters gameplay screen directly
    return redirect(f"/mp/play/{room_code}")


@mp_bp.route("/mp/lobby/<room_code>")
def mp_lobby(room_code):
    """Host waiting screen. Checks if a guest has joined."""
    user_id = session.get('user_id')
    if not user_id:
        return redirect("/login")

    game_room = MultiplayerSession.query.filter_by(room_code=room_code).first()

    if not game_room:
        return redirect("/")

    #Only host gets to access their own lobby
    if game_room.host_id != user_id:
        return redirect("/")

    # If guest has joined, auto-redirect host to gameplay!
    if game_room.status == "active":
        return redirect(f"/mp/play/{room_code}")

    return render_template("mp_lobby.html", room_code=room_code)

@mp_bp.route("/mp/play/<room_code>")
def mp_play(room_code):
    user_id = session.get('user_id')
    if not user_id:
        return redirect("/login")

    game_room = MultiplayerSession.query.filter_by(room_code=room_code).first()

    if not game_room:
        return redirect("/")

    is_host = (user_id == game_room.host_id)
    if user_id != game_room.host_id and user_id != game_room.guest_id:
        return redirect("/")

    my_deck = game_room.host_deck if is_host else game_room.guest_deck
    opponent_deck = game_room.guest_deck if is_host else game_room.host_deck

    # 1. CHECK GAME OVER FIRST! (Applies whether status is completed or active)
    if len(my_deck) == 0 or len(opponent_deck) == 0 or game_room.status == "completed":
        if game_room.status != "completed":
            # Set winner in DB
            if len(my_deck) > 0:
                game_room.winner_id = user_id
            else:
                game_room.winner_id = game_room.guest_id if is_host else game_room.host_id
            game_room.status = "completed"
            db.session.commit()

        return redirect(f"/mp/game_over/{room_code}")

    # 2. Check round result redirect only if game is still going
    if game_room.status == "round_result":
        return redirect(f"/mp/round_result/{room_code}")

    # Fetch top card for current round
    my_card = get_card(game_room.deck_theme, my_deck[0])
    is_my_turn = (game_room.turn == 1 and is_host) or (game_room.turn == 2 and not is_host)

    return render_template(
        "mp_play.html",
        room_code=room_code,
        my_card=my_card,
        cards_left=len(my_deck),
        opp_cards_left=len(opponent_deck),
        is_my_turn=is_my_turn
    )


@mp_bp.route("/mp/choice/<room_code>", methods=["POST"])
def mp_choice(room_code):
    user_id = session.get('user_id')
    if not user_id:
        return redirect("/login")

    game_room = MultiplayerSession.query.filter_by(room_code=room_code).first()
    if not game_room or game_room.status != "active":
        return redirect("/")

    is_host = (user_id == game_room.host_id)
    
    # Validation: Ensure it's actually the user's turn
    if (game_room.turn == 1 and not is_host) or (game_room.turn == 2 and is_host):
        return redirect(f"/mp/play/{room_code}")

    stat_name = request.form.get('stat_choice')
    
    # Map stat string to its corresponding integer key for game_engine
    stat_to_num = {
        "matches": 1, "not_outs": 2, "runs_scored": 3, "highest": 4, "bat_avg": 5,
        "balls_faced": 6, "bat_sr": 7, "hundreds": 8, "fifties": 9, "balls_bowled": 10,
        "runs_given": 11, "catches": 12, "wickets": 13, "ball_avg": 14, "economy": 15,
        "ball_sr": 16, "best_figures": 17, "five_w": 18
    }
    
    stat_num = stat_to_num.get(stat_name, 1)

    host_deck = list(game_room.host_deck)
    guest_deck = list(game_room.guest_deck)

    # Fetch full card dicts to pass into game_engine.evaluate
    host_card = get_card(game_room.deck_theme, host_deck[0])
    guest_card = get_card(game_room.deck_theme, guest_deck[0])

    # Evaluate winner (1 = Host/Player 1 wins, 0 = Guest/Player 2 wins)
    winner = game_engine.evaluate(stat_num, host_card, guest_card)

    # Pop top cards
    h_card_id = host_deck.pop(0)
    g_card_id = guest_deck.pop(0)

    if winner == 1:
        # Host wins round -> gets both cards
        host_deck.extend([h_card_id, g_card_id])
        game_room.last_winner = 'host'
        game_room.turn = 1  # Winner gets next turn
    else:
        # Guest wins round -> gets both cards
        guest_deck.extend([h_card_id, g_card_id])
        game_room.last_winner = 'guest'
        game_room.turn = 2  # Winner gets next turn

    # Save state to DB
    game_room.host_deck = host_deck
    game_room.guest_deck = guest_deck
    game_room.last_stat = stat_name
    game_room.host_card_played = host_card
    game_room.guest_card_played = guest_card
    game_room.status = "round_result"
    db.session.commit()

    return redirect(f"/mp/round_result/{room_code}")

@mp_bp.route("/mp/round_result/<room_code>")
def mp_round_result(room_code):
    user_id = session.get('user_id')
    if not user_id:
        return redirect("/login")

    game_room = MultiplayerSession.query.filter_by(room_code=room_code).first()
    if not game_room:
        return redirect("/")

    is_host = (user_id == game_room.host_id)
    my_card = game_room.host_card_played if is_host else game_room.guest_card_played
    opp_card = game_room.guest_card_played if is_host else game_room.host_card_played

    stat_name = game_room.last_stat or "matches"
    
    # Determine winner message relative to current user
    if (game_room.last_winner == 'host' and is_host) or (game_room.last_winner == 'guest' and not is_host):
        result_text = "You Won!"
    else:
        result_text = "You Lost!"
    my_deck_len = len(game_room.host_deck) if is_host else len(game_room.guest_deck)
    opp_deck_len = len(game_room.guest_deck) if is_host else len(game_room.host_deck)

    return render_template(
        "mp_battle_result.html",
        room_code=room_code,
        result=result_text,
        stat_choice=stat_name,
        player_card=my_card,
        ai_card=opp_card,
        player_deck_size=my_deck_len,
        ai_deck_size=opp_deck_len
    )

@mp_bp.route("/mp/next_round/<room_code>")
def mp_next_round(room_code):
    user_id = session.get('user_id')
    if not user_id:
        return redirect("/login")

    game_room = MultiplayerSession.query.filter_by(room_code=room_code).first()
    if game_room:
        # Only switch back to active if the game wasn't already completed!
        if game_room.status == "round_result":
            game_room.status = "active"
            db.session.commit()

    return redirect(f"/mp/play/{room_code}")

@mp_bp.route("/mp/game_over/<room_code>")
def mp_game_over(room_code):
    user_id = session.get('user_id')
    if not user_id:
        return redirect("/login")

    game_room = MultiplayerSession.query.filter_by(room_code=room_code).first()
    if not game_room:
        return redirect("/")

    # Determine winner based on who still has cards in their deck
    if game_room.winner_id==user_id:
        result_title = "Victory!"
        message = "Dont get excited that was a fluke"
    else:
        result_title = "Defeat"
        message = "Skill issue. You are a noob"

    # Mark room as completed in database

    return render_template(
        "mp_game_over.html",
        result_title=result_title,
        message=message
    )
