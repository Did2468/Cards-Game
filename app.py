from flask import Flask, render_template, request, session, redirect
import json
import random
import string
import game_setup
import game_engine
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)
app.secret_key = "Passwordis2468"

# Attach socket handler extension wrapper
socketio = SocketIO(app, cors_allowed_origins="*")

# In-memory session pool mapping matchmaking profiles
active_rooms = {}
cards = {}

def preload_cards():
    global cards
    try:
        with open('ipl_stats.json', 'r') as file:
            players_list = json.load(file)
        cards = {player["id"]: player for player in players_list}
    except FileNotFoundError:
        cards = {}

preload_cards()

def generate_room_code():
    while True:
        code = ''.join(random.choices(string.ascii_uppercase, k=4))
        if code not in active_rooms:
            return code

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/toss")
def toss_page():
    return render_template('toss.html')

@app.route("/toss_result", methods=["POST"])
def toss_result():
    global cards
    user_choice = int(request.form['choice'])
    deck_theme = request.form['deck_theme']
    cards = game_setup.theme_selector(deck_theme)
    result = game_setup.toss_logic(user_choice)
    session['turn'] = result
    return render_template('toss_result.html', won=result)

@app.route("/ultimate_team", methods=["GET"])
def setup_ultimate_team():
    role = request.args.get('role', 'p1')
    room_code = request.args.get('room_code', '').strip().upper()
    if role == 'p2' and not room_code:
        return redirect('/')
    return render_template('ultimate-team.html', cards=cards, role=role, room_code=room_code)

@app.route("/start_game_ultimate", methods=["POST"])
def start_game_ultimate():
    raw_player_deck = request.form.getlist('player_ids')
    p1_deck = [int(p_id) for p_id in raw_player_deck if p_id.strip().isdigit()]
    random.shuffle(p1_deck)
    
    room_code = generate_room_code()
    active_rooms[room_code] = {
        'p1_sid': None, 'p2_sid': None,
        'p1_deck': p1_deck, 'p2_deck': [],
        'turn': 1, 'last_stat_name': None, 'last_stat_choice': None, 'chosen_by': None
    }
    
    session['room_code'] = room_code
    session['role'] = 'p1'
    return render_template('lobby.html', room_code=room_code, role='p1')

@app.route("/join_room", methods=["POST"])
def join_room_endpoint():
    room_code = request.form.get('room_code', '').strip().upper()
    raw_player_deck = request.form.getlist('player_ids')
    p2_deck = [int(p_id) for p_id in raw_player_deck if p_id.strip().isdigit()]
    random.shuffle(p2_deck)
    
    if room_code not in active_rooms:
        return "Room code not found!", 404
    if active_rooms[room_code]['p2_sid'] is not None or len(active_rooms[room_code]['p2_deck']) > 0:
        return "This room is already full!", 400
        
    active_rooms[room_code]['p2_deck'] = p2_deck
    session['room_code'] = room_code
    session['role'] = 'p2'
    return render_template('lobby.html', room_code=room_code, role='p2')

@app.route("/setup")
def setup_page():
    max_cards = len(cards)
    return render_template('setup.html', max_cards=max_cards)

@app.route("/start_game", methods=["POST"])
def start_game():
    card_num = int(request.form['num_cards'])
    player1, player2 = game_setup.distribute_logic(len(cards), card_num)
    session['player_deck'] = player1
    session['ai_deck'] = player2
    session['round_num'] = 1
    return redirect('/play')

@app.route("/play")
def play():
    room_code = session.get('room_code')
    role = session.get('role')
    
    # Fallback default path rules if playing Classic Singleplayer Mode
    if not room_code or room_code not in active_rooms:
        player_deck = session.get('player_deck', [])
        ai_deck = session.get('ai_deck', [])
        turn = session.get('turn', 0)

        if len(player_deck) == 0 or len(ai_deck) == 0:
            return redirect('/game_over')
            
        player_card = cards[player_deck[0]]
        if turn == 1:
            return render_template('player_turn.html', player_card=player_card, cards_left=len(player_deck), ai_cards_left=len(ai_deck), room_code='')
        else:
            return render_template('ai_turn.html', player_card=player_card, cards_left=len(player_deck), ai_cards_left=len(ai_deck), room_code='')

    # Online multiplayer state tree handling
    room = active_rooms[room_code]
    p1_deck = room['p1_deck']
    p2_deck = room['p2_deck']
    turn = room['turn']
    
    if len(p1_deck) == 0 or len(p2_deck) == 0:
        return redirect('/game_over')
        
    my_card_id = p1_deck[0] if role == 'p1' else p2_deck[0]
    my_card = cards[my_card_id]
    
    my_cards_left = len(p1_deck) if role == 'p1' else len(p2_deck)
    opp_cards_left = len(p2_deck) if role == 'p1' else len(p1_deck)
    
    is_my_turn = (turn == 1 and role == 'p1') or (turn == 2 and role == 'p2')
    
    if is_my_turn:
        return render_template('player_turn.html', player_card=my_card, cards_left=my_cards_left, ai_cards_left=opp_cards_left, room_code=room_code)
    else:
        return render_template('ai_turn.html', player_card=my_card, cards_left=my_cards_left, ai_cards_left=opp_cards_left, room_code=room_code)

@app.route("/player_choice", methods=["POST"])
def player_choice():
    room_code = session.get('room_code')
    role = session.get('role')
    stat_name = request.form['stat_choice']
    
    stat_to_num = {
        "matches": 1, "not_outs": 2, "runs_scored": 3, "highest": 4, "bat_avg": 5,
        "balls_faced": 6, "bat_sr": 7, "hundreds": 8, "fifties": 9, "balls_bowled": 10,
        "runs_given": 11, "catches": 12, "wickets": 13, "ball_avg": 14, "economy": 15,
        "ball_sr": 16, "best_figures": 17, "five_w": 18
    }
    
    # Check if this is an online matchmaking session
    if room_code in active_rooms:
        active_rooms[room_code]['last_stat_choice'] = stat_to_num[stat_name]
        active_rooms[room_code]['last_stat_name'] = stat_name
        active_rooms[room_code]['chosen_by'] = role
        socketio.emit('round_evaluated', room=room_code)
        return redirect('/battle_result')
        
    # Standard single player fallback logic
    session['last_stat_choice'] = stat_to_num[stat_name]
    session['last_stat_name'] = stat_name
    session['choosen_by'] = 'player'
    return redirect('/battle_result')

@app.route("/ai_choice", methods=["POST"])
def ai_choice():
    stat_num = random.randint(1, 10)
    stat_name = game_engine.STAT_CHOICES[stat_num]
    session['last_stat_choice'] = stat_num
    session['last_stat_name'] = stat_name
    session['choosen_by'] = 'ai'
    return redirect('/battle_result')

@app.route("/battle_result")
def battle_result():
    room_code = session.get('room_code')
    role = session.get('role')
    
    if room_code and room_code in active_rooms:
        return render_template('battle_result.html', room_code=room_code, role=role)
        
    # Single player evaluation logic
    player_deck = session['player_deck']
    ai_deck = session['ai_deck']
    player_card = cards[player_deck[0]]
    ai_card = cards[ai_deck[0]]
    
    stat_choice = session['last_stat_choice']
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
        
    session['player_deck'] = player_deck
    session['ai_deck'] = ai_deck
    session['turn'] = next_turn
    
    return render_template('battle_result.html', player_card=player_card, ai_card=ai_card, stat_choice=game_engine.STAT_CHOICES[stat_choice], result=result_message, player_deck_size=len(player_deck), ai_deck_size=len(ai_deck), room_code='')

@app.route("/next_round")
def next_round():
    return redirect('/play')

@app.route("/game_over")
def game_over():
    room_code = session.get('room_code')
    role = session.get('role')
    
    if room_code and room_code in active_rooms:
        room = active_rooms[room_code]
        p1_len = len(room['p1_deck'])
        if (role == 'p1' and p1_len == 0) or (role == 'p2' and p1_len > 0):
            return render_template('game_over.html', winner='Your Friend', message='Better luck next time!!')
        return render_template('game_over.html', winner='You', message='Congratulations')

    player_deck = session.get('player_deck', [])
    if len(player_deck) == 0:
        winner = 'Computer'
        message = "Better luck next time!!"
    else:
        winner = "You"
        message = "Congratulations"
    return render_template('game_over.html', winner=winner, message=message)

# --- WebSocket Communications Logic ---

@socketio.on('join_lobby')
def handle_lobby_joining(data):
    room = data['room_code']
    role = data['role']
    join_room(room)
    
    if room in active_rooms:
        if role == 'p1':
            active_rooms[room]['p1_sid'] = request.sid
        elif role == 'p2':
            active_rooms[room]['p2_sid'] = request.sid
            
        if active_rooms[room]['p1_sid'] and active_rooms[room]['p2_sid']:
            emit('redirect_to_game', room=room)

@socketio.on('join_battle_room')
def handle_battle_room_sync(data):
    join_room(data['room_code'])

@socketio.on('advance_next_round')
def handle_round_advancement(data):
    room_code = data['room_code']
    if room_code not in active_rooms:
        return
        
    room = active_rooms[room_code]
    if room['last_stat_choice'] is not None:
        p1_card = cards[room['p1_deck'][0]]
        p2_card = cards[room['p2_deck'][0]]
        
        winner = game_engine.evaluate(room['last_stat_choice'], p1_card, p2_card)
        p_card = room['p1_deck'].pop(0)
        a_card = room['p2_deck'].pop(0)
        
        if winner == 1:
            room['p1_deck'].append(p_card)
            room['p1_deck'].append(a_card)
            room['turn'] = 1 
        else:
            room['p2_deck'].append(p_card)
            room['p2_deck'].append(a_card)
            room['turn'] = 2
            
        room['last_stat_choice'] = None
        room['last_stat_name'] = None
        
    emit('redirect_to_play', room=room_code)

if __name__ == "__main__":
    # Swap out app.run for socketio.run execution loop context
    #socketio.run(app, debug=True)
    port = int(os.environ.get('PORT', 5000))
    socketio.run(host='0.0.0.0', port=port)
	
