from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Integer, Text, DateTime, Column
from datetime import datetime
from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, Text, UniqueConstraint, Table, String
from sqlalchemy.orm import relationship, backref



db = SQLAlchemy()
blocklist = Table("blocklist", 
                  db.metadata,
                  Column("blocker_id", Integer, ForeignKey("user.id"), primary_key=True), 
                  Column("blocked_id", Integer, ForeignKey("user.id"), primary_key=True))
followers = db.Table("followers", 
                  Column("follower_id", Integer, ForeignKey("user.id")), 
                  Column("followed_id", Integer, ForeignKey("user.id")))
class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String(20), unique=True, nullable = False)
    created_at = Column(DateTime, default=datetime.now)
    full_name = Column(String(20))
    bio = Column(String(100))
    pfp = Column(Text)
    password_hash = Column(Text)
    is_admin = Column(Boolean, default = False)
    polls = relationship("Poll", back_populates="author")
    votes = relationship("Vote", back_populates="user")
    comments = relationship("Comment", back_populates="author")
    def Setpassword(self, password):
        self.password_hash = generate_password_hash(password)
    def Checkpassword(self, password):
        return check_password_hash(self.password_hash, password)
    
    def getpfp(self):
        if self.pfp:
            return f"/static/uploads/pfp/{self.pfp}"
        else:
            return f"/static/uploads/pfp/default.jpg"
    blocked = relationship(
        "User", secondary=blocklist, 
        primaryjoin=(blocklist.c.blocker_id == id),
        secondaryjoin=(blocklist.c.blocked_id == id),
        backref=db.backref("blocked_by", lazy="dynamic"),
        lazy="dynamic"
    )
    followed = relationship(
        "User", secondary=followers, 
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref("followers", lazy="dynamic"),
        lazy="dynamic"
    )

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user) 
    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0      
    def is_blocking(self, user):
        return self.blocked.filter(blocklist.c.blocked_id == user.id).count() > 0
    def block(self, user):
        if not self.is_blocking(user):
            self.blocked.append(user)
            db.session.commit()
    def unblock(self, user):
        if self.is_blocking(user):
            self.blocked.remove(user)
            db.session.commit()
    def get_rank(self):
        poll_count = Poll.query.filter_by(user_id=self.id).count()
        vote_count = Vote.query.filter_by(user_id=self.id).count()
        comment_count = Comment.query.filter_by(user_id=self.id).count()

        total_score = poll_count + vote_count + comment_count

        if total_score < 5:
            return "Newbie"
        elif total_score < 20:
            return "Active"
        elif total_score < 50:
            return "Expert"
        else:
            return "Divine"


    def get_rank_color(self):
        rank = self.get_rank()
        if rank == "Newbie": return "gray"
        if rank == "Active": return "blue"
        if rank == "Expert": return "purple"
        if rank == "Divine": return "gold"
        return "black"

        
class CommentReaction(db.Model):
    __tablename__ = "comment_reaction"

    id = Column(Integer, primary_key=True)
    reaction_type = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    comment_id = Column(Integer, ForeignKey("comment.id"), nullable=False)
    user = relationship("User")
    comment = relationship("Comment", back_populates="reactions")

    __table_args__ = (
        UniqueConstraint('user_id', 'comment_id', name='user_comment_reaction_uc'),
    )





class Vote(db.Model):
    __tablename__ = "vote"

    id = Column(Integer, primary_key=True)

    created_at = Column(DateTime, default=datetime.now)

    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    poll_id = Column(Integer, ForeignKey("poll.id"), nullable=False)
    option_id = Column(Integer, ForeignKey("poll_option.id"), nullable=False)

    user = relationship("User", back_populates="votes")
    poll = relationship("Poll", back_populates="votes")
    option = relationship("PollOption", back_populates="votes")
    __table_args__ = (
        UniqueConstraint('user_id', 'poll_id', name='user_poll_uc'),
    )


class Comment(db.Model):
    __tablename__ = "comment"
        
    id = Column(Integer, primary_key=True)
    content = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    reactions = relationship("CommentReaction", back_populates="comment", cascade="all, delete-orphan")
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    poll_id = Column(Integer, ForeignKey("poll.id"), nullable=False)
    author = relationship("User", back_populates="comments")
    poll = relationship("Poll", back_populates="comments")
    is_pinned =  Column(Boolean, default=False)
    is_authorliked = Column(Boolean, default=False)
    
    def get_likes_count(self):
        return CommentReaction.query.filter_by(comment_id = self.id, reaction_type = "like").count()
    def get_dislikes_count(self):
        return CommentReaction.query.filter_by(comment_id = self.id, reaction_type = "dislike").count()



class PollOption(db.Model):
    __tablename__ = "poll_option"

    id = Column(Integer, primary_key=True)
    text = Column(String(50), nullable=False)
    poll_id = Column(Integer, ForeignKey("poll.id"), nullable=False)
    poll = relationship("Poll", back_populates="options")
    votes = relationship("Vote", back_populates="option", cascade="all, delete-orphan")


class Poll(db.Model):
    __tablename__ = "poll"

    id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    description = Column(String(120))
    created_at = Column(DateTime, default=datetime.now)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    end_date = Column(DateTime, nullable=True)
    author = relationship("User", back_populates="polls")
    comments = relationship("Comment", back_populates="poll", cascade="all, delete-orphan")
    options = relationship("PollOption", back_populates="poll", cascade="all, delete-orphan")
    votes = relationship("Vote", back_populates="poll", cascade="all, delete-orphan")
    def is_active(self):
        if self.end_date is None:
            return True
        return datetime.now() < self.end_date

    def getvotecount(self):
        return len(self.votes)

    



class Report(db.Model):
    __tablename__ = 'report'

    id = Column(Integer, primary_key=True)
    reason = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    status = Column(String(20), default='pending', nullable=False)  

    reporter_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    reporter = relationship('User', foreign_keys=[reporter_id])

    poll_id = Column(Integer, ForeignKey('poll.id'), nullable=True)
    poll = relationship('Poll')

    comment_id = Column(Integer, ForeignKey('comment.id'), nullable=True)
    comment = relationship('Comment')

    reported_user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    reported_user = relationship('User', foreign_keys=[reported_user_id])


class Notification(db.Model):
    __tablename__ = 'notification'

    id = Column(Integer, primary_key=True)
    message = Column(Text)
    is_read = Column(Boolean)
    created_at = Column(DateTime, default=datetime.now)

    recipient_id = Column(Integer, ForeignKey('user.id'))
    recipient = relationship("User", backref="notifications", foreign_keys=[recipient_id])
    poll_id = Column(Integer, ForeignKey('poll.id'))
    
class PollUploads(db.Model):
    __tablename__ = 'poll_uploads'

    id = Column(Integer, primary_key=True)
    filename = Column(Text, nullable=False)
    file_type = Column(Text, nullable=False)
    poll_id = Column(Integer, ForeignKey('poll.id'))
    poll = relationship("Poll", backref= db.backref("uploads", cascade="all, delete-orphan"))

    