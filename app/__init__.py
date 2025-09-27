from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app.routes import auth, main, polls
from app.models import User, db

login_manager = LoginManager()
def createapp():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pollvoter.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    login_manager.init_app(app)
    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(polls)
    @login_manager.user_loader
    def load_user(userid):
        return User.query.get(int(userid))
    return app