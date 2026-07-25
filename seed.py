import json
import os

from flask import Flask
from database import db
from models import IplPlayer, OdiPlayer, T20iPlayer, TestPlayer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SOURCES = {
	'ipl': ('ipl_stats.json', IplPlayer),
	'odi': ('odi_stats.json', OdiPlayer),
	't20i': ('t20i_stats.json', T20iPlayer),
	'test': ('test_stats.json', TestPlayer),
}


def build_app():
	app = Flask(__name__)
	app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'game_data.db')
	db.init_app(app)
	return app


def load_theme(theme, filename, model):
	path = os.path.join(BASE_DIR, 'data', filename)
	with open(path, 'r') as f:
		players = json.load(f)

	model.query.delete()  # wipe so re-running never leaves stale/duplicate rows

	for p in players:
		row = model(
			id=p['id'],
			name=p['name'],
			matches=p.get('matches', 0),
			not_outs=p.get('not_outs', 0),
			runs_scored=p.get('runs_scored', 0),
			highest=p.get('highest', 0),
			bat_avg=p.get('bat_avg', 0.0),
			balls_faced=p.get('balls_faced', 0),
			bat_sr=p.get('bat_sr', 0.0),
			hundreds=p.get('hundreds', 0),
			fifties=p.get('fifties', 0),
			balls_bowled=p.get('balls_bowled', 0),
			runs_given=p.get('runs_given', 0),
			catches=p.get('catches', 0),
			wickets=p.get('wickets', 0),
			ball_avg=p.get('ball_avg', 0.0),
			economy=p.get('economy', 0.0),
			ball_sr=p.get('ball_sr', 0.0),
			best_w=p.get('best_w', 0),
			best_r=p.get('best_r', 0),
			five_w=p.get('five_w', 0),
		)
		db.session.add(row)

	db.session.commit()
	print(f"{theme}: loaded {len(players)} players into '{model.__tablename__}'")

def seed_if_empty():
	for theme,(filename,model) in SOURCES.items():
		if model.query.count()==0:
			load_theme(theme,filename,model)
		else:
			print("skipping")

def main():
	app = build_app()
	with app.app_context():
		db.create_all()
		for theme, (filename, model) in SOURCES.items():
			load_theme(theme, filename, model)


if __name__ == "__main__":
	main()
