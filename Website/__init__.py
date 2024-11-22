from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager, current_user
import logging
from flask_migrate import Migrate

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
DB_NAME = 'database.db'
login_manager = LoginManager()

def create_db(app):
    """Create the database if it doesn't exist."""
    if not path.exists('website/' + DB_NAME):
        with app.app_context():  
            db.create_all()  
        app.logger.info('Created Database!')
    else:
        app.logger.info('Database already exists.')

def create_app():
    """Initialize and configure the Flask application."""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'obfdbgbkpwfduvbfd'  
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'  
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Configure logging
    logging.basicConfig(level=logging.DEBUG)
    app.logger.addHandler(logging.StreamHandler())
    app.logger.setLevel(logging.DEBUG)

    app.logger.debug("App created")
    
    # Import and register blueprints
    from .views import views
    from .auth import auth
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    # Import models
    from .models import User, Bet, BetParticipation, BetResult  # Replace with actual model names

    # Create the database
    create_db(app)

    # Setup login manager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  

    @login_manager.user_loader
    def load_user(id):
        """Load user by ID for Flask-Login."""
        return User.query.get(int(id))

    @app.context_processor
    def inject_user():
        """Inject the current user into the template context."""
        return dict(current_user=current_user) 

    return app
