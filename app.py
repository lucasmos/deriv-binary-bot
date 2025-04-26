import os
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
from app.extensions import db, csrf
from auth.models import User
from ai.model import load_ai_model

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)
    migrate = Migrate(app, db)
    
    # Initialize login manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Load AI model
    @app.before_first_request
    def load_model():
        app.ai_model = load_ai_model(app.config['AI_MODEL_PATH'])
        from bot.core.trading_engine import TradingEngine
        app.trading_engine = TradingEngine

    # Register blueprints
    from auth.routes import auth_bp
    from bot.routes import bot_bp
    from marketplace.routes import marketplace_bp
    from payments.routes import payments_bp
    from admin.routes import admin_bp
    from payments.webhooks import webhooks_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(bot_bp, url_prefix='/bot')
    app.register_blueprint(marketplace_bp, url_prefix='/marketplace')
    app.register_blueprint(payments_bp, url_prefix='/payments')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(webhooks_bp, url_prefix='/webhooks')

    # Register error handlers
    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    # Initialize payment providers
    from payments.services import PaymentService
    app.payment_service = PaymentService()

    # Initialize trading services
    from bot.services import TradingService
    app.trading_service = TradingService

    # CLI commands
    from app.commands import register_commands
    register_commands(app)

    return app

from app import models  # noqa