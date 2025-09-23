from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, db, Poll, Comment, Vote

auth = Blueprint("auth", __name__)
main = Blueprint("main", __name__)
polls = Blueprint("polls", __name__)

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



@polls.route("/create_poll", methods = ["GET", "POST"])
@login_required
def create_poll():
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        newpoll = Poll(title = title, description = description, user_id = current_user.id)
        db.session.add(newpoll)
        db.session.commit()
        return redirect(url_for("polls.poll_detail", poll_id = newpoll.id))
    return render_template("create_poll.html")

@polls.route("/poll/<int:poll_id>")
@login_required
def poll_detail(poll_id):
    poll = Poll.query.get_or_404(poll_id)
    user_vote = Vote.query.filter_by(user_id = current_user.id, poll_id = poll_id).first()
    return render_template("poll_detail.html", poll = poll, user_vote = user_vote)

@polls.route("/polls")
@login_required
def listpolls():
    page = request.args.get("page", 1, type=int)
    polls = Poll.query.order_by(Poll.created_at.desc()).paginate(page=page, per_page=2)
    return render_template("polls.html", polls = polls)






@polls.route("/poll/<int:poll_id>/vote", methods=["POST"])
@login_required
def vote(poll_id):
    poll = Poll.query.get_or_404(poll_id)
    vote_value = request.form.get("vote")

    if vote_value not in ["yes", "no"]:
        flash("Invalid vote option")
        return redirect(url_for("polls.poll_detail", poll_id=poll_id))

    existing_vote = Vote.query.filter_by(user_id = current_user.id, poll_id = poll_id).first()

    if existing_vote:
        flash("You have already voted")
        return redirect(url_for("polls.poll_detail", poll_id=poll_id))

    new_vote = Vote(
        vote=(vote_value == "yes"),
        user_id=current_user.id,
        poll_id=poll_id
    )

    db.session.add(new_vote)
    db.session.commit()

    flash("Thank you for voting!")
    return redirect(url_for("polls.poll_detail", poll_id=poll_id))



@polls.route("/poll/<int:poll_id>/comment", methods = ["POST"])
@login_required
def add_comment(poll_id):
    poll = Poll.query.get_or_404(poll_id)
    content = request.form.get("content")
    if not content:
        flash("Please fill out the blank")
        return redirect(url_for("polls.poll_detail", poll_id = poll_id))
    new_comment = Comment(content = content, user_id = current_user.id, poll_id = poll_id)
    db.session.add(new_comment)
    db.session.commit()
    flash("Comment added")
    return redirect(url_for("polls.poll_detail", poll_id = poll_id))

@main.route("/")
def home():
    latest_polls = Poll.query.order_by(Poll.created_at.desc()).limit(5).all()
    return render_template("home.html", polls = latest_polls)
@polls.route("/my_polls")
@login_required
def my_polls():
    page = request.args.get("page", 1, type=int)
    user_polls = Poll.query.filter_by(user_id = current_user.id).order_by(Poll.created_at.desc()).paginate(page=page, per_page=2)
    return render_template("my_polls.html", polls = user_polls)




