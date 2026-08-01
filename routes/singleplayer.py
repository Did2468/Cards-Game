import random
from flask import Blueprint, render_template, request, session, redirect
from database import db
from models import User
import game_setup
import game_engine
from utils.helpers import (
    get_cards, get_card, get_card_count, get_current_game, create_game
)

sp_bp = Blueprint('singleplayer', __name__)

# Home page
@sp_bp.route("/")
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

# toss page
@sp_bp.route("/toss")
def toss_page():
	return render_template('toss.html')

# toss processing
@sp_bp.route("/toss_result", methods=["POST"])
def toss_result():
	user_choice = int(request.form['choice'])
	deck_theme = request.form['deck_theme']
	result = game_setup.toss_logic(user_choice)
	create_game(deck_theme=deck_theme, turn=result)
	return render_template('toss_result.html', won=result)

# deck support added ultimate team like thingy
@sp_bp.route("/ultimate_team", methods=["POST", "GET"])
def setup_ultimate_team():
	cards = get_cards('ipl')
	return render_template('ultimate-team.html', cards=cards)

# ultimate team start_game_ultimate
@sp_bp.route("/start_game_ultimate", methods=["POST", "GET"])
def start_game_ultimate():
	raw_player_deck = request.form.getlist('player_ids')
	player1 = [int(p_id) for p_id in raw_player_deck if p_id.strip().isdigit()]
	random.shuffle(player1)
	player2 = game_setup.choose_ai_ultimate_team(player1, get_card_count('ipl'))
	create_game(deck_theme='ipl', turn=1, player_deck=player1, ai_deck=player2)
	return redirect('/play')

# cards setup page
@sp_bp.route("/setup")
def setup_page():
	game = get_current_game()
	max_cards = get_card_count(game.deck_theme) if game else 0
	return render_template('setup.html', max_cards=max_cards)

# processing the setup
@sp_bp.route("/start_game", methods=["POST"])
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
@sp_bp.route("/play")
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

@sp_bp.route("/player_choice", methods=["POST"])
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

@sp_bp.route("/ai_choice", methods=["POST"])
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

@sp_bp.route("/battle_result")
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

@sp_bp.route("/next_round")
def next_round():
	return redirect('/play')

@sp_bp.route("/game_over")
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
