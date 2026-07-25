from flask import Flask, render_template, request, session, redirect
import random
import uuid
import os
import game_setup
import game_engine
from database import db
from models import IplPlayer, OdiPlayer, T20iPlayer, TestPlayer, GameSession

app = Flask(__name__)
app.secret_key = "Passwordis2468"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'game_data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
	db.create_all()  # only creates tables that dont exist yet.doesnt touch my existing tables

# theme -> model. Run seed_from_json.py first to populate these tables.
THEME_MODELS = {
	'ipl': IplPlayer,
	'odi': OdiPlayer,
	't20i': T20iPlayer,
	'test': TestPlayer,
}


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


# Home page
@app.route("/")
def home():
	return render_template('home.html')


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
	app.run(debug=True)
#	port = int(os.environ.get('PORT', 5000))
#	app.run(host='0.0.0.0', port=port)
	
