from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Integer, Text, DateTime, Column

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