from flask import Blueprint, render_template, request, session
from database import db
from models import User

auth_bp = Blueprint('auth', __name__)

#Login Page
@auth_bp.route("/login")
def login():
	return render_template("login.html",error=None)

#Login handle
@auth_bp.route("/login-handle",methods=["POST","GET"])
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
@auth_bp.route("/register")
def register():
	return render_template("register.html",error=None)

#register handling page
@auth_bp.route("/register-handle",methods=["POST","GET"])
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
