from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Integer, Text, DateTime, Column
from datetime import datetime
from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship



db = SQLAlchemy()
class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(Text, unique=True, nullable = False)
    created_at = Column(DateTime, default=datetime.now)
    full_name = Column(Text)
    bio = Column(Text)
    pfp = Column(Text)
    password_hash = Column(Text)

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


class Poll(db.Model):
    __tablename__ = "poll"

    id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    votes = relationship("Vote", back_populates="poll", lazy=True, cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="poll", lazy=True, cascade="all, delete-orphan")
    author = relationship("User", back_populates="polls")
    def getvotecount(self):
        return Vote.query.filter_by(poll_id = self.id).count()
    
    def getyescount(self):
        return Vote.query.filter_by(poll_id = self.id, vote = True).count()
    
    def getnocount(self):
        return Vote.query.filter_by(poll_id = self.id, vote = False).count()
    
    def getyespercentage(self):
        total = self.getvotecount()
        if total == 0:
            return 0
        return (self.getyescount()/total)*100
    
    def getnopercentage(self):
        total = self.getvotecount()
        if total == 0:
            return 0
        return (self.getnocount()/total)*100
        






class Vote(db.Model):
    __tablename__ = "vote"

    id = Column(Integer, primary_key=True)
    vote = Column(Boolean, nullable=False) 
    created_at = Column(DateTime, default=datetime.now)

    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    poll_id = Column(Integer, ForeignKey("poll.id"), nullable=False)

    user = relationship("User", back_populates="votes")
    poll = relationship("Poll", back_populates="votes")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'poll_id', name='user_poll_uc'),
    )


class Comment(db.Model):
    __tablename__ = "comment"
        
    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    poll_id = Column(Integer, ForeignKey("poll.id"), nullable=False)
    author = relationship("User", back_populates="comments")
    poll = relationship("Poll", back_populates="comments")
