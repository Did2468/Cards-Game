from database import db
from datetime import datetime


class PlayerStatsMixin:
	"""Shared columns for every format table. Each class that mixes this in
	gets its OWN copy of these columns in its OWN table — nothing is shared
	at the db level, this just avoids retyping 20 columns four times."""

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100), nullable=False)
	matches = db.Column(db.Integer, default=0)
	not_outs = db.Column(db.Integer, default=0)
	runs_scored = db.Column(db.Integer, default=0)
	highest = db.Column(db.Integer, default=0)
	bat_avg = db.Column(db.Float, default=0.0)
	balls_faced = db.Column(db.Integer, default=0)
	bat_sr = db.Column(db.Float, default=0.0)
	hundreds = db.Column(db.Integer, default=0)
	fifties = db.Column(db.Integer, default=0)
	balls_bowled = db.Column(db.Integer, default=0)
	runs_given = db.Column(db.Integer, default=0)
	catches = db.Column(db.Integer, default=0)
	wickets = db.Column(db.Integer, default=0)
	ball_avg = db.Column(db.Float, default=0.0)
	economy = db.Column(db.Float, default=0.0)
	ball_sr = db.Column(db.Float, default=0.0)
	best_w = db.Column(db.Integer, default=0)
	best_r = db.Column(db.Integer, default=0)
	five_w = db.Column(db.Integer, default=0)

	def to_dict(self):
		return {
			'id': self.id,
			'name': self.name,
			'matches': self.matches,
			'not_outs': self.not_outs,
			'runs_scored': self.runs_scored,
			'highest': self.highest,
			'bat_avg': self.bat_avg,
			'balls_faced': self.balls_faced,
			'bat_sr': self.bat_sr,
			'hundreds': self.hundreds,
			'fifties': self.fifties,
			'balls_bowled': self.balls_bowled,
			'runs_given': self.runs_given,
			'catches': self.catches,
			'wickets': self.wickets,
			'ball_avg': self.ball_avg,
			'economy': self.economy,
			'ball_sr': self.ball_sr,
			'best_w': self.best_w,
			'best_r': self.best_r,
			'five_w': self.five_w
		}


class IplPlayer(PlayerStatsMixin, db.Model):
	__tablename__ = 'ipl_players'


class OdiPlayer(PlayerStatsMixin, db.Model):
	__tablename__ = 'odi_players'


class T20iPlayer(PlayerStatsMixin, db.Model):
	__tablename__ = 't20i_players'


class TestPlayer(PlayerStatsMixin, db.Model):
	__tablename__ = 'test_players'


class GameSession(db.Model):
	__tablename__ = 'game_sessions'

	id = db.Column(db.Integer, primary_key=True)
	session_id = db.Column(db.String(100), unique=True, nullable=False)

	player_deck = db.Column(db.JSON, nullable=False)
	ai_deck = db.Column(db.JSON, nullable=False)
	turn = db.Column(db.Integer, default=0)
	round_num = db.Column(db.Integer, default=1)
	deck_theme = db.Column(db.String(20))

	last_stat_choice = db.Column(db.Integer)
	last_stat_name = db.Column(db.String(50))
	chosen_by = db.Column(db.String(20))

	created_at = db.Column(db.DateTime, default=datetime.utcnow)
	updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
