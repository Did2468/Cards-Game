from flask import Flask, render_template,request,session,redirect
import json
from game_engine import evaluate
import random
import game_setup
import game_engine
import os
app = Flask(__name__)
app.secret_key = "Passwordis2468"

with open('player_stats.json','r') as file:
	players_list = json.load(file)

cards = {player["id"]: player for player in players_list}

#Home page 
@app.route("/")
def home():
	return render_template('home.html')

#toss page
@app.route("/toss")
def toss_page():
	return render_template('toss.html')


#toss processing
@app.route("/toss_result",methods=["POST"])
def toss_result():
	user_choice = int(request.form['choice'])
	result = game_setup.toss_logic(user_choice)
	
	session['turn'] = result
	return render_template('toss_result.html',won=result)

# cards setup page
@app.route("/setup")
def setup_page():
	max_cards = len(cards)
	return render_template('setup.html',max_cards = max_cards)

#processing the setup
@app.route("/start_game",methods=["POST"])
def start_game():
	card_num = int(request.form['num_cards'])
	player1,player2 = game_setup.distribute_logic(len(cards),card_num)
	
	session['player_deck'] = player1
	session['ai_deck'] = player2
	session['round_num'] = 1
	return redirect('/play')

#Rest of the game
@app.route("/play")
def play():
	player_deck = session.get('player_deck',[])
	ai_deck = session.get('ai_deck',[])
	turn = session.get('turn',0)

	if len(player_deck)==0 or len(ai_deck)==0:
		return redirect('/game_over')
	player_card_id = player_deck[0]
	ai_card_id = ai_deck[0]
	player_card = cards[player_card_id]
	ai_card = cards[ai_card_id]
	
	if(turn==1):
		return render_template('player_turn.html',player_card=player_card,cards_left=len(player_deck))
	else:
		return render_template('ai_turn.html',player_card=player_card,cards_left=len(player_deck))

@app.route("/player_choice",methods=["POST"])
def player_choice():
	stat_name = request.form['stat_choice']
	stat_to_num = {
		"rank":1,"matches":2,"runs":3,"balls":4,"fifties":5,"hundreds":6,"sr":7,
		"wickets":8,"econ":9,"best_figures":10
		}
	stat_num = stat_to_num[stat_name]
	session['last_stat_choice'] = stat_num
	session['last_stat_name'] = stat_name
	session['choosen_by'] = 'player'
	
	return redirect('/battle_result')

@app.route("/ai_choice",methods=["POST"])
def ai_choice():
	stat_num = random.randint(1,10)
	STAT_CHOICES = {
        	1: "rank", 2: "matches", 3: "runs", 4: "balls", 5: "fifties", 
        	6: "hundreds", 7: "sr", 8: "wickets", 9: "econ", 10: "best_figures"
   	}
	stat_name = STAT_CHOICES[stat_num]
	session['last_stat_choice'] = stat_num
	session['last_stat_name'] = stat_name
	session['choosen_by'] = 'ai'
	
	return redirect('/battle_result')

@app.route("/battle_result")
def battle_result():
	player_deck = session['player_deck']
	ai_deck = session['ai_deck']
	player_card = cards[player_deck[0]]
	ai_card = cards[ai_deck[0]]
	
	stat_choice = session['last_stat_choice']
	winner = game_engine.evaluate(stat_choice,player_card,ai_card)
	
	p_card = player_deck.pop(0)
	a_card = ai_deck.pop(0)

	if winner == 1:
		player_deck.append(p_card)
		player_deck.append(a_card)
		result_message  = "You Won this Round!!"
		next_turn = 1
	else:
		ai_deck.append(p_card)
		ai_deck.append(a_card)
		result_message = "You Lost this round!!"
		next_turn = 0
	session['player_deck'] = player_deck
	session['ai_deck'] = ai_deck
	session['turn'] = next_turn
	
	return render_template('battle_result.html',player_card=player_card,ai_card=ai_card,stat_choice=game_engine.STAT_CHOICES[stat_choice],result=result_message,player_deck_size=len(player_deck),ai_deck_size=len(ai_deck))

@app.route("/next_round")
def next_round():
	return redirect('/play')

@app.route("/game_over")
def game_over():
	player_deck = session.get('player_deck',[])
	ai_deck = session.get('ai_deck',[])
	if(len(player_deck)==0):
		winner = 'Computer'
		message = "Better luck next time!!"
	else:
		winner = "You"
		message = "Congratulations"
	return render_template('game_over.html',winner=winner,message=message)
if __name__=="__main__":
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port)
