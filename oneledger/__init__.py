from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # Function name of the login route
login_manager.login_message_category = 'info' # Bootstrap class for flash messages

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # Import and register blueprints here
    # Example:
    # from oneledger.auth.routes import auth_bp
    # app.register_blueprint(auth_bp)

    # from oneledger.main.routes import main_bp # If you have a main blueprint
    # app.register_blueprint(main_bp)

    from .auth.routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from .main.routes import main_bp # Import and register the main blueprint
    app.register_blueprint(main_bp)

    from .accounting.routes import accounting_bp # Import and register the accounting blueprint
    app.register_blueprint(accounting_bp, url_prefix='/accounting')

    from .payroll.routes import payroll_bp # Import and register the payroll blueprint
    app.register_blueprint(payroll_bp, url_prefix='/payroll')


    return app
