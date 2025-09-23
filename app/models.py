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
    

    password_hash = Column(Text)

    def Setpassword(self, password):
        self.password_hash = generate_password_hash(password)
    def Checkpassword(self, password):
        return check_password_hash(self.password_hash, password)
    



class Poll(db.Model):
    __tablename__ = "poll"

    id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    votes = relationship("Vote", backref="poll", lazy=True, cascade="all, delete-orphan")
    comments = relationship("Comment", backref="poll", lazy=True, cascade="all, delete-orphan")
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
