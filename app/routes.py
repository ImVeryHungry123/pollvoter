from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
import click
from functools import wraps
from .models import User, db, Poll, Comment, Vote, CommentReaction, PollOption,Report
import os
from werkzeug.utils import secure_filename

auth = Blueprint("auth", __name__)
main = Blueprint("main", __name__)
polls = Blueprint("polls", __name__)
admin = Blueprint("admin", __name__)

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





@polls.route("/poll/<int:poll_id>")
@login_required
def poll_detail(poll_id):
    poll = Poll.query.get_or_404(poll_id)
    user_vote = Vote.query.filter_by(user_id = current_user.id, poll_id = poll_id).first()
    return render_template("poll_detail.html", poll = poll, user_vote = user_vote)






@polls.route("/poll/<int:poll_id>/vote", methods=["POST"])
@login_required
def vote(poll_id):
    poll = Poll.query.get_or_404(poll_id)

    option_id = request.form.get("option_id")
    if not option_id:
        return redirect(url_for("polls.poll_detail", poll_id = poll_id))


    existing_vote = Vote.query.filter_by(user_id = current_user.id, poll_id = poll_id).first()

    if existing_vote:
        flash("You have already voted")
        return redirect(url_for("polls.poll_detail", poll_id=poll_id))

    new_vote = Vote(

        user_id = current_user.id,
        poll_id = poll_id, 
        option_id = option_id
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

@auth.route("/logout", methods = ["GET", "POST"])
def logout():
    logout_user()
    return redirect(url_for("main.home"))



@main.route('/profile')
@login_required
def profile():
    user_polls = Poll.query.filter_by(user_id=current_user.id).order_by(
        Poll.created_at.desc()
    ).all()

    polls_count = len(user_polls)

    total_votes = Vote.query.join(Poll).filter(
        Poll.user_id == current_user.id
    ).count()

    total_comments = Comment.query.filter_by(
        user_id=current_user.id
    ).count()

    return render_template(
        'profile.html',
        user_polls=user_polls,
        polls_count=polls_count,
        total_votes=total_votes,
        total_comments=total_comments
    )

@main.route('/edit_profile', methods = ["GET", "POST"])
@login_required
def edit_profile():
    if request.method == "POST":
        current_user.full_name = request.form.get("full_name")
        current_user.bio = request.form.get("bio")
        if "pfp" in request.files:
            file = request.files["pfp"]
            
            if file and file.filename:
                pfp_folder = current_app.config['PFP_FOLDER']
                os.makedirs(pfp_folder,exist_ok=True)
                
                if current_user.pfp:
                    oldfilepath = os.path.join(current_app.config["PFP_FOLDER"], current_user.pfp)
                    if os.path.exists(oldfilepath):
                        os.remove(oldfilepath)
                
                filename = secure_filename(f"user_{current_user.id}_{file.filename}")
                file.save(os.path.join(
                        current_app.config['PFP_FOLDER'], 
                        filename
                    ))
                current_user.pfp = filename
        db.session.commit()
        flash("Profile updated!")
        return redirect(url_for("main.profile"))
    return render_template("edit_profile.html")

@main.route('/user/<username>')
def user_profile(username):
   
    user = User.query.filter_by(username=username).first_or_404()
    

    user_polls = Poll.query.filter_by(user_id=user.id).order_by(
        Poll.created_at.desc()
    ).all()
    
   
    polls_count = len(user_polls)
    
  
    total_votes = Vote.query.join(Poll).filter(Poll.user_id == user.id).count()
    
   
    total_comments = Comment.query.filter_by(user_id=user.id).count()
    
    return render_template(
        'user_profile.html',
        user=user,
        user_polls=user_polls,
        polls_count=polls_count,
        total_votes=total_votes,
        total_comments=total_comments
    )

@polls.route("/poll/<int:poll_id>/edit", methods = ["GET", "POST"])
@login_required
def edit_poll(poll_id):
    poll = Poll.query.get_or_404(poll_id)
    if poll.author != current_user:
        flash("You don't have access to edit this poll")
        return redirect(url_for("polls.my_polls"))
    if request.method == "POST":
        poll.title = request.form["title"]
        poll.description = request.form["description"]
        db.session.commit()
        flash("Changes successful!")
        return redirect(url_for("polls.my_polls"))
    return render_template("edit_poll.html", poll = poll)

@polls.route("/poll/<int:poll_id>/delete", methods = ["POST"])
@login_required
def delete_poll(poll_id):
    poll = Poll.query.get_or_404(poll_id)
    if poll.author != current_user:
        flash("You don't have access to delete this poll")
        return redirect(url_for("polls.my_polls"))
    db.session.delete(poll)
    db.session.commit()
    flash("Deleted poll!")
    return redirect(url_for("polls.my_polls"))





@polls.route("/comment/<int:comment_id>/edit", methods=["POST"])
@login_required
def edit_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)

    if comment.author != current_user:
        flash("You are not authorized to edit this comment.")
        return redirect(url_for("polls.poll_detail", poll_id=comment.poll_id))

    new_content = request.form.get("content")

    if new_content:
        comment.content = new_content
        db.session.commit()
        flash("Comment updated successfully.")
    else:
        flash("Comment content cannot be empty.")

    return redirect(url_for("polls.poll_detail", poll_id=comment.poll_id))


@polls.route("/comment/<int:comment_id>/delete", methods=["POST"])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    poll_id = comment.poll_id

    if comment.author != current_user:
        flash("You are not authorized to delete this comment.")
        return redirect(url_for("polls.poll_detail", poll_id=poll_id))

    db.session.delete(comment)
    db.session.commit()
    flash("Comment has been deleted.")

    return redirect(url_for("polls.poll_detail", poll_id=poll_id))

@polls.route("/comment/<int:comment_id>/react", methods=["POST"])
@login_required
def react_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    reaction_type = request.form.get("reaction")
    if reaction_type not in ["like", "dislike"]:
        flash("Invalid reaction")
        return redirect(url_for("polls.poll_detail", poll_id=comment.poll_id))
    existing_reaction = CommentReaction.query.filter_by(user_id = current_user.id, comment_id = comment_id).first()
    if existing_reaction:
        if existing_reaction.reaction_type == reaction_type:
            db.session.delete(existing_reaction)
        else:
            existing_reaction.reaction_type = reaction_type
    else:
        new_reaction = CommentReaction(reaction_type = reaction_type, user_id = current_user.id, comment_id = comment_id)
        db.session.add(new_reaction)
    db.session.commit()
    return redirect(url_for("polls.poll_detail", poll_id=comment.poll_id))
            

    
@polls.route("/create_poll", methods=["GET", "POST"])
@login_required
def create_poll():
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        options_texts = request.form.getlist("options")

        if not title or len(options_texts) < 2:
            flash("Please provide a title and at least two options.")
            return render_template("create_poll.html")

        new_poll = Poll(title=title, description=description, author=current_user)
        db.session.add(new_poll)

        for option_text in options_texts:
            if option_text:
                option = PollOption(text=option_text, poll=new_poll)
                db.session.add(option)

        db.session.commit()
        flash("Poll created successfully!")
        return redirect(url_for("polls.poll_detail", poll_id=new_poll.id))

    return render_template("create_poll.html")

@main.route("/block/<username>", methods=["POST"])
@login_required
def block(username):
    user = User.query.filter_by(username = username).first_or_404()
    if user == current_user:
        return redirect(url_for("main.user_profile", username = username))
    current_user.block(user)
    return redirect(url_for("main.user_profile", username = username))

@main.route("/unblock/<username>", methods=["POST"])
@login_required
def unblock(username):
    user = User.query.filter_by(username = username).first_or_404()
    if user == current_user:
        return redirect(url_for("main.user_profile", username = username))
    current_user.unblock(user)
    return redirect(url_for("main.user_profile", username = username))


@polls.route('/polls')
@login_required
def listpolls():
    sort_by = request.args.get('sort_by', 'newest', type=str)
    page = request.args.get('page', 1, type=int)

    blocked_ids = [user.id for user in current_user.blocked]
    blocked_by_ids = [user.id for user in current_user.blocked_by]
    exclude_ids = blocked_ids + blocked_by_ids

    query = Poll.query.filter(Poll.user_id.notin_(exclude_ids))

    if sort_by == 'popular':
        query = query.outerjoin(Vote).group_by(Poll.id).order_by(db.func.count(Vote.id).desc())
    elif sort_by == 'discussed':
        query = query.outerjoin(Comment).group_by(Poll.id).order_by(db.func.count(Comment.id).desc())
    else:
        query = query.order_by(Poll.created_at.desc())

    polls = query.paginate(page=page, per_page=5)

    return render_template('polls.html', polls=polls, sort_by=sort_by)


def admin_required(f):
    @wraps(f)
    def decorate_function(*args,**kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You have no access to this page.')
            return redirect(url_for('main.home'))
        return f(*args,**kwargs)
    return decorate_function

@admin.route("/admin")
@login_required
@admin_required
def dashboard():
    reports = Report.query.filter_by(status = "pending").order_by(Report.created_at.desc()).all()
    return render_template("admin_panel.html", reports = reports)

@admin.route("/admin/report/dismiss/<int:report_id>", methods = ["POST"])
@login_required
@admin_required
def dismiss(report_id):
    report = Report.query.get_or_404(report_id)
    report.status = "resolved"
    db.session.commit()
    return redirect(url_for("admin.dashboard"))

@admin.route("/admin/delete_poll/<int:poll_id>/<int:report_id>", methods = ["POST"])
@login_required
@admin_required
def admin_delete_poll(poll_id, report_id):
    poll = Poll.query.get_or_404(poll_id)
    db.session.delete(poll)
    report = Report.query.get_or_404(report_id)
    report.status = "resolved"
    db.session.commit()
    return redirect(url_for("admin.dashboard"))



@admin.route("/admin/delete_comment/<int:comment_id>/<int:report_id>", methods = ["POST"])
@login_required
@admin_required
def admin_delete_comment(comment_id, report_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    report = Report.query.get_or_404(report_id)
    report.status = "resolved"
    db.session.commit()
    return redirect(url_for("admin.dashboard"))


@polls.route("/poll/<int:poll_id>/report", methods = ["GET", "POST"])
@login_required
def report_poll(poll_id):
    poll = Poll.query.get_or_404(poll_id)
    if request.method == "POST":
        reason = request.form.get("reason")
        new_report = Report(
            reason = reason, reporter_id = current_user.id, poll_id = poll.id, reported_user_id = poll.author.id
            
        )
        db.session.add(new_report)
        db.session.commit()
        return redirect(url_for("polls.poll_detail", poll_id = poll.id))
    return render_template("report_form.html", poll = poll)

@polls.route("/comment/<int:comment_id>/report", methods = ["GET", "POST"])
@login_required
def report_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if request.method == "POST":
        reason = request.form.get("reason")
        new_report = Report(
            reason = reason, reporter_id = current_user.id, comment_id = comment.id, reported_user_id = comment.author.id
            
        )
        db.session.add(new_report)
        db.session.commit()
        return redirect(url_for("polls.poll_detail", poll_id = comment.poll.id))
    return render_template("report_form.html", comment = comment)

