import os

from flask import Flask
from database import db
from models import IplPlayer, OdiPlayer, T20iPlayer, TestPlayer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

THEME_MODELS = {
	'ipl': IplPlayer,
	'odi': OdiPlayer,
	't20i': T20iPlayer,
	'test': TestPlayer,
}

# (field name, prompt text, type, default)
STAT_FIELDS = [
	('matches', "Matches", int, 0),
	('not_outs', "Not outs", int, 0),
	('runs_scored', "Runs scored", int, 0),
	('highest', "Highest score", int, 0),
	('bat_avg', "Batting average", float, 0.0),
	('balls_faced', "Balls faced", int, 0),
	('bat_sr', "Batting strike rate", float, 0.0),
	('hundreds', "Hundreds", int, 0),
	('fifties', "Fifties", int, 0),
	('balls_bowled', "Balls bowled", int, 0),
	('runs_given', "Runs given", int, 0),
	('catches', "Catches", int, 0),
	('wickets', "Wickets", int, 0),
	('ball_avg', "Bowling average", float, 0.0),
	('economy', "Economy", float, 0.0),
	('ball_sr', "Bowling strike rate", float, 0.0),
	('best_w', "Best bowling - wickets", int, 0),
	('best_r', "Best bowling - runs", int, 0),
	('five_w', "Five-wicket hauls", int, 0),
]


def build_app():
	app = Flask(__name__)
	app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'game_data.db')
	db.init_app(app)
	return app


def prompt_theme():
	while True:
		theme = input(f"Which format? ({'/'.join(THEME_MODELS.keys())}): ").strip().lower()
		if theme in THEME_MODELS:
			return theme
		print(f"'{theme}' isn't one of {list(THEME_MODELS.keys())}, try again.")


def prompt_value(label, cast, default):
	raw = input(f"{label} [{default}]: ").strip()
	if raw == "":
		return default
	try:
		return cast(raw)
	except ValueError:
		print(f"Couldn't read that as a {cast.__name__}, using default {default}.")
		return default


def next_id(model):
	max_id = db.session.query(db.func.max(model.id)).scalar()
	return (max_id or 0) + 1


def main():
	app = build_app()
	with app.app_context():
		db.create_all()

		theme = prompt_theme()
		model = THEME_MODELS[theme]

		name = input("Player name: ").strip()
		while not name:
			name = input("Name can't be blank. Player name: ").strip()

		stats = {}
		print(f"\nEnter stats for {name} (press Enter to accept the default shown):")
		for field, label, cast, default in STAT_FIELDS:
			stats[field] = prompt_value(label, cast, default)

		new_id = next_id(model)
		player = model(id=new_id, name=name, **stats)
		db.session.add(player)
		db.session.commit()

		print(f"\nAdded '{name}' to '{model.__tablename__}' with id {new_id}.")


if __name__ == "__main__":
	main()
