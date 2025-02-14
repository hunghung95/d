from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from app.admin import admin_bp as admin_blueprint
    app.register_blueprint(admin_blueprint)

    return app