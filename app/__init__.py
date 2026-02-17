from flask import Flask, request, session
import click

from flask_babel import Babel


from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app.routes import auth, main, polls,admin
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
    app.config["BABEL_DEFAULT_LOCALE"] = "en"
    app.config["LANGUAGES"] = ["en", "hi", "zh", "ru", "uk", "fr", "es", "de", "ja", "ko", "it"]
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

  
    def get_locale():

        if 'lang' in session:
            return session['lang']
        return request.accept_languages.best_match(app.config["LANGUAGES"])
    babel = Babel(app, locale_selector = get_locale)
    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(polls)
    app.register_blueprint(admin)
    @login_manager.user_loader
    def load_user(userid):
        return User.query.get(int(userid))
    return app

app = create_app()
@app.cli.command("make_admin")
@click.argument("username")
def make_admin(username):
    with app.app_context():
        user = User.query.filter_by(username = username).first()
        if user:
            user.is_admin = True
            db.session.commit()
        