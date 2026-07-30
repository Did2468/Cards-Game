from flask import Flask, render_template, request, session, redirect
from dotenv import load_dotenv
import random
import uuid
import os
import game_setup
import game_engine
import seed
import string
from database import db
from models import IplPlayer, OdiPlayer, T20iPlayer, TestPlayer, GameSession,User,MultiplayerSession

# Load environment variables from .env file locally
load_dotenv()

app = Flask(__name__)
app.secret_key = "Passwordis2468"

#Fetching the db from neon
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
	db.create_all()  # only creates tables that dont exist yet.doesnt touch my existing tables
	seed.seed_if_empty() 	# solves the issue where when the server goes inactive it loses the .db file so need to restart this eveyrtime
# theme -> model. Run seed_from_json.py first to populate these tables.
THEME_MODELS = {
	'ipl': IplPlayer,
	'odi': OdiPlayer,
	't20i': T20iPlayer,
	'test': TestPlayer,
}
def generate_room_code(length=4):
    """Generates a unique 4-character uppercase room code."""
    characters = string.ascii_uppercase + string.digits
    while True:
        code = ''.join(random.choices(characters, k=length))
        existing = MultiplayerSession.query.filter_by(room_code=code).first()
        if not existing:
            return code
def get_cards(theme):
	model = THEME_MODELS[theme]
	return {p.id: p.to_dict() for p in model.query.all()}


def get_card(theme, card_id):
	model = THEME_MODELS[theme]
	player = db.session.get(model, card_id)
	return player.to_dict() if player else None


def get_card_count(theme):
	return THEME_MODELS[theme].query.count()


def get_current_game():
	"""The Flask session cookie only stores a game_id pointer — the actual
	deck/turn/round state lives in the GameSession row in game_data.db."""
	game_id = session.get('game_id')
	if not game_id:
		return None
	return GameSession.query.filter_by(session_id=game_id).first()


def create_game(deck_theme, turn, player_deck=None, ai_deck=None, round_num=1):
	game = GameSession(
		session_id=uuid.uuid4().hex,
		deck_theme=deck_theme,
		turn=turn,
		round_num=round_num,
		player_deck=player_deck or [],
		ai_deck=ai_deck or []
	)
	db.session.add(game)
	db.session.commit()
	session['game_id'] = game.session_id
	return game
def deal_mp_decks(theme="ipl", deck_size=12):
    total_cards = get_card_count(theme)
    host_cards, guest_cards = game_setup.distribute_logic(total_cards, deck_size)
    return host_cards, guest_cards

# Home page
@app.route("/")
def home():
	user_id = session.get('user_id')
	current_user = None
	if user_id:
		db_user = db.session.get(User,user_id)
		if db_user:
			current_user = {
				'username':db_user.username,
				'is_guest':False	
			}
	if not current_user:
		if 'guest_id' not in session:
			session['guest_id'] = f"Guest_{random.randint(1000,9999)}"
			current_user = {
				'username':session['guest_id'],
				'is_guest':True
			}
	return render_template('home.html',user=current_user)

#Login Page
@app.route("/login")
def login():
	return render_template("login.html",error=None)
#Login handle
@app.route("/login-handle",methods=["POST","GET"])
def login_handle():
	username = request.form.get("username","").strip()
	password = request.form.get("password","").strip()

	user = User.query.filter_by(username=username).first()
	if user and user.check_pass:
		session["user_id"] = user.id
		return render_template("home.html",user=user)
	else:
		return render_template("login.html",error="Invalid username or password")

#Register page
@app.route("/register")
def register():
	return render_template("register.html",error=None)

#register handling page
@app.route("/register-handle",methods=["POST","GET"])
def register_handle():
	username = request.form.get("username","").strip()
	password = request.form.get("password","").strip()
	existing_user = User.query.filter_by(username=username).first()
	if existing_user:
		return render_template("register.html",error="Username already taken try taking a new one")
	new_user = User(username=username)
	new_user.set_password(password)
	db.session.add(new_user)
	db.session.commit()
	return render_template("login.html",error="Account Created Succesffully.Please Login!!")

#Multiplayer Features
@app.route("/mp/handle_create", methods=["POST"])
def handle_create_room():
    """Generates a room code, sets current user as host, and sends them to the lobby."""
    user_id = session.get('user_id')
    if not user_id:
        return render_template("login.html", error="Please log in to create a room!")

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

@app.route("/mp/create")
def create_room_page():
    user_id = session.get('user_id')
    if not user_id:
        return render_template("login.html", error="Please log in to create a room!")
    
    return render_template("create_room_theme.html")

@app.route("/mp/create/size")
def create_room_size():
    user_id = session.get('user_id')
    if not user_id:
        return render_template("login.html", error="Please log in to create a room!")

    deck_theme = request.args.get("deck_theme", "ipl")
    
    # Calculate exact max cards for this theme (each player gets up to half the pool)
    max_cards = get_card_count(deck_theme)

    return render_template("create_room_size.html", deck_theme=deck_theme, max_cards=max_cards)

@app.route("/mp/handle_join", methods=["POST"])
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


@app.route("/mp/lobby/<room_code>")
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

@app.route("/mp/play/<room_code>")
def mp_play(room_code):
    user_id = session.get('user_id')
    if not user_id:
        return redirect("/login")

    # Fetch room from the db
    game_room = MultiplayerSession.query.filter_by(room_code=room_code).first()

    if not game_room or game_room.status == "completed":
        return redirect("/")

    # Security check Ensure the user belongs to this match
    if user_id != game_room.host_id and user_id != game_room.guest_id:
        return redirect("/")

    # Determine guests and hosts with the players
    is_host = (user_id == game_room.host_id)
    my_deck = game_room.host_deck if is_host else game_room.guest_deck
    opponent_deck = game_room.guest_deck if is_host else game_room.host_deck

    # Check for game over
    if len(my_deck) == 0 or len(opponent_deck) == 0:
        return redirect(f"/mp/game_over/{room_code}")

    # Fetch card data using your existing get_card helper
    my_card = get_card(game_room.deck_theme, my_deck[0])
    
    # Check whose turn it is 1 = Host turn, 2 = Guest turn
    is_my_turn = (game_room.turn == 1 and is_host) or (game_room.turn == 2 and not is_host)

    return render_template(
        "mp_play.html",
        room_code=room_code,
        my_card=my_card,
        cards_left=len(my_deck),
        opp_cards_left=len(opponent_deck),
        is_my_turn=is_my_turn
    )

@app.route("/mp/choice/<room_code>", methods=["POST"])
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

    db.session.commit()

    return redirect(f"/mp/round_result/{room_code}")
@app.route("/mp/round_result/<room_code>")
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
        winner_text = "You Won!"
    else:
        winner_text = "You Lost!"

    my_stat_val = my_card.get(stat_name, 0) if my_card else 0
    opp_stat_val = opp_card.get(stat_name, 0) if opp_card else 0

    # Auto-refresh for opponent while they wait
    is_my_turn = (game_room.turn == 1 and is_host) or (game_room.turn == 2 and not is_host)

    return render_template(
        "mp_battle_result.html",
        room_code=room_code,
        winner_text=winner_text,
        stat_name=stat_name.replace('_', ' ').title(),
        my_card=my_card,
        opp_card=opp_card,
        my_stat_val=my_stat_val,
        opp_stat_val=opp_stat_val,
        auto_refresh=not is_my_turn
    )
@app.route("/mp/game_over/<room_code>")
def mp_game_over(room_code):
    user_id = session.get('user_id')
    if not user_id:
        return redirect("/login")

    game_room = MultiplayerSession.query.filter_by(room_code=room_code).first()
    if not game_room:
        return redirect("/")

    is_host = (user_id == game_room.host_id)
    my_deck = game_room.host_deck if is_host else game_room.guest_deck

    # Determine winner based on who still has cards in their deck
    if len(my_deck) > 0:
        result_title = "Victory!"
        message = "Dont get excited that was a fluke"
    else:
        result_title = "Defeat"
        message = "Skill issue. You are a noob"

    # Mark room as completed in database
    game_room.status = "completed"
    db.session.commit()

    return render_template(
        "mp_game_over.html",
        result_title=result_title,
        message=message
    )
# toss page
@app.route("/toss")
def toss_page():
	return render_template('toss.html')


# toss processing
@app.route("/toss_result", methods=["POST"])
def toss_result():
	user_choice = int(request.form['choice'])
	deck_theme = request.form['deck_theme']
	result = game_setup.toss_logic(user_choice)
	create_game(deck_theme=deck_theme, turn=result)
	return render_template('toss_result.html', won=result)


# deck support added ultimate team like thingy
@app.route("/ultimate_team", methods=["POST", "GET"])
def setup_ultimate_team():
	cards = get_cards('ipl')
	return render_template('ultimate-team.html', cards=cards)


# ultimate team start_game_ultimate
@app.route("/start_game_ultimate", methods=["POST", "GET"])
def start_game_ultimate():
	raw_player_deck = request.form.getlist('player_ids')
	player1 = [int(p_id) for p_id in raw_player_deck if p_id.strip().isdigit()]
	random.shuffle(player1)
	player2 = game_setup.choose_ai_ultimate_team(player1, get_card_count('ipl'))
	create_game(deck_theme='ipl', turn=1, player_deck=player1, ai_deck=player2)
	return redirect('/play')


# cards setup page
@app.route("/setup")
def setup_page():
	game = get_current_game()
	max_cards = get_card_count(game.deck_theme) if game else 0
	return render_template('setup.html', max_cards=max_cards)


# processing the setup
@app.route("/start_game", methods=["POST"])
def start_game():
	game = get_current_game()
	card_num = int(request.form['num_cards'])
	total_cards = get_card_count(game.deck_theme)
	player1, player2 = game_setup.distribute_logic(total_cards, card_num)

	game.player_deck = player1
	game.ai_deck = player2
	game.round_num = 1
	db.session.commit()
	return redirect('/play')


# Rest of the game
@app.route("/play")
def play():
	game = get_current_game()
	player_deck = game.player_deck if game else []
	ai_deck = game.ai_deck if game else []
	turn = game.turn if game else 0

	if len(player_deck) == 0 or len(ai_deck) == 0:
		return redirect('/game_over')

	player_card = get_card(game.deck_theme, player_deck[0])
	ai_card = get_card(game.deck_theme, ai_deck[0])

	if turn == 1:
		return render_template('player_turn.html', player_card=player_card, cards_left=len(player_deck), ai_cards_left=len(ai_deck))
	else:
		return render_template('ai_turn.html', player_card=player_card, cards_left=len(player_deck), ai_cards_left=len(ai_deck))


@app.route("/player_choice", methods=["POST"])
def player_choice():
	game = get_current_game()
	stat_name = request.form['stat_choice']
	stat_to_num = {
		"matches": 1, "not_outs": 2, "runs_scored": 3, "highest": 4, "bat_avg": 5,
		"balls_faced": 6, "bat_sr": 7, "hundreds": 8, "fifties": 9, "balls_bowled": 10,
		"runs_given": 11, "catches": 12, "wickets": 13, "ball_avg": 14, "economy": 15,
		"ball_sr": 16, "best_figures": 17, "five_w": 18
	}
	game.last_stat_choice = stat_to_num[stat_name]
	game.last_stat_name = stat_name
	game.chosen_by = 'player'
	db.session.commit()
	return redirect('/battle_result')


@app.route("/ai_choice", methods=["POST"])
def ai_choice():
	game = get_current_game()
	stat_num = random.randint(1, 18)
	STAT_CHOICES = {
		1: "matches", 2: "not_outs", 3: "runs_scored", 4: "highest", 5: "bat_avg",
		6: "balls_faced", 7: "bat_sr", 8: "hundreds", 9: "fifties", 10: "balls_bowled",
		11: "runs_given", 12: "catches", 13: "wickets", 14: "ball_avg", 15: "economy",
		16: "ball_sr", 17: "best_figures", 18: "five_w"
	}
	stat_name = STAT_CHOICES[stat_num]
	game.last_stat_choice = stat_num
	game.last_stat_name = stat_name
	game.chosen_by = 'ai'
	db.session.commit()
	return redirect('/battle_result')


@app.route("/battle_result")
def battle_result():
	game = get_current_game()
	player_deck = list(game.player_deck)
	ai_deck = list(game.ai_deck)
	player_card = get_card(game.deck_theme, player_deck[0])
	ai_card = get_card(game.deck_theme, ai_deck[0])

	stat_choice = game.last_stat_choice
	winner = game_engine.evaluate(stat_choice, player_card, ai_card)

	p_card = player_deck.pop(0)
	a_card = ai_deck.pop(0)

	if winner == 1:
		player_deck.append(p_card)
		player_deck.append(a_card)
		result_message = "You Won this Round!!"
		next_turn = 1
	else:
		ai_deck.append(p_card)
		ai_deck.append(a_card)
		result_message = "You Lost this round!!"
		next_turn = 0

	game.player_deck = player_deck
	game.ai_deck = ai_deck
	game.turn = next_turn
	db.session.commit()

	return render_template('battle_result.html', player_card=player_card, ai_card=ai_card, stat_choice=game_engine.STAT_CHOICES[stat_choice], result=result_message, player_deck_size=len(player_deck), ai_deck_size=len(ai_deck))


@app.route("/next_round")
def next_round():
	return redirect('/play')


@app.route("/game_over")
def game_over():
	game = get_current_game()
	player_deck = game.player_deck if game else []
	if len(player_deck) == 0:
		winner = 'Computer'
		message = "Better luck next time!!"
	else:
		winner = "You"
		message = "Congratulations"
	if game:
		db.session.delete(game)
		db.session.commit()
	session.pop('game_id',None)
	return render_template('game_over.html', winner=winner, message=message)


if __name__ == "__main__":
#	app.run(debug=True)
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port)
