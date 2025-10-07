from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app.routes import auth, main, polls
from app.models import User, db
from flask_migrate import Migrate
login_manager = LoginManager()
migrate = Migrate()
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pollvoter.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config["UPLOAD_FOLDER"] = "static/uploads"
    app.config["PFP_FOLDER"] =  "app/static/uploads/pfp"
    
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(polls)
    @login_manager.user_loader
    def load_user(userid):
        return User.query.get(int(userid))
    return app

app = create_app()