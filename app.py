from flask import Flask
from dotenv import load_dotenv
import os

from database import db
import seed

# Clean blueprint imports made possible by routes/__init__.py
from routes import auth_bp, sp_bp, mp_bp

# Load environment variables from .env file locally
load_dotenv()

app = Flask(__name__)
app.secret_key = "Passwordis2468"

# Fetching the db from neon
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(sp_bp)
app.register_blueprint(mp_bp)

with app.app_context():
	db.create_all()  # only creates tables that dont exist yet.doesnt touch my existing tables
	seed.seed_if_empty() 	# solves the issue where when the server goes inactive it loses the .db file so need to restart this eveyrtime

if __name__ == "__main__":
#	app.run(debug=True)
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port)
