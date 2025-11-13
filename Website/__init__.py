from flask import Flask, g, session
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager, current_user
import logging
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
DB_NAME = 'database.db'

def create_app():
    """Initialize and configure the Flask application."""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'obfdbgbkpwfduvbfd'  
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'  
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    logging.basicConfig(level=logging.DEBUG)
    app.logger.addHandler(logging.StreamHandler())
    app.logger.setLevel(logging.DEBUG)

    app.logger.debug("App created")
    
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from .views import views
    from .auth import auth
    from .models import User 

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    @login_manager.user_loader
    def load_user(id):
        """Load user by ID for Flask-Login."""
        return User.query.get(int(id))

    @app.before_request
    def load_user_before_request():
        user_id = session.get('user_id')
        if user_id is None:
            g.user = None
        else:
            g.user = User.query.get(user_id)

    @app.context_processor
    def inject_user_and_guest():
        return dict(user=g.user)

    return app