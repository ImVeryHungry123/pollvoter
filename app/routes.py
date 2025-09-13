from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, db

auth = Blueprint("auth", __name__)

@auth.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username = username).first()
        if user and user.Checkpassword(password):
            login_user(user)
            return redirect(url_for("main.home"))
    return render_template("login.html")

@auth.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username = username).first()
        if user:
            flash("Sorry, this username is taken.")
        else:
            newuser = User(username = username)
            newuser.Setpassword(password)
            db.session.add(newuser)
            db.session.commit()
            login_user(newuser)
            return redirect(url_for("main.home"))
    return render_template("register.html")
