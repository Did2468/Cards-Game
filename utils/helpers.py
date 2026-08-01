import random
import string
import uuid
from flask import session
from database import db
from models import IplPlayer, OdiPlayer, T20iPlayer, TestPlayer, GameSession, MultiplayerSession
import game_setup

# theme -> model. Run seed_from_json.py first to populate these tables.
THEME_MODELS = {
	'ipl': IplPlayer,
	'odi': OdiPlayer,
	't20i': T20iPlayer,
	'test': TestPlayer,
}

def cleanup_stale_mp_sessions():
    try:
        MultiplayerSession.query.filter_by(status="completed").delete()
        db.session.commit()
    except Exception as e:
        db.session.rollback()

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
