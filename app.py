import os
from U import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from ai.pipeline import ContinuousLearning
import asyncio
import threading
from celery import Celery

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    login.login_view = 'auth.login'
    celery.conf.update(app.config)
    
    # Register blueprints
    register_blueprints(app)
    
    # Initialize AI components
    initialize_ai(app)
    
    # Configure logging
    configure_logging(app)
    
    # Start background tasks
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        start_background_tasks(app)
    
    return app

def register_blueprints(app):
    """Register all application blueprints"""
    from auth.routes import auth_bp
    from main.routes import main_bp
    from marketplace.routes import marketplace_bp
    from payments.routes import payments_bp
    from bot.core.routes import bot_bp
    from admin.routes import admin_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(marketplace_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(bot_bp)
    app.register_blueprint(admin_bp)

def initialize_ai(app):
    """Initialize AI components"""
    from ai.model import TradingAIModel
    app.ai_model = TradingAIModel()
    
    # Load production model if exists
    model_path = os.path.join(app.config['AI_MODEL_PATH'], 'model.h5')
    if os.path.exists(model_path):
        app.ai_model.load(model_path)

def configure_logging(app):
    """Configure application logging"""
    import logging
    from logging.handlers import RotatingFileHandler
    
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/deriv_bot.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Deriv Bot startup')

def start_background_tasks(app):
    """Start background tasks in separate threads"""
    with app.app_context():
        # Continuous learning pipeline
        cl = ContinuousLearning()
        thread = threading.Thread(target=asyncio.run, args=(cl.daily_improvement_cycle(),))
        thread.daemon = True
        thread.start()
        
        # Market data sync
        from bot.jobs.data_sync import start_data_sync
        sync_thread = threading.Thread(target=start_data_sync)
        sync_thread.daemon = True
        sync_thread.start()

app = create_app()

@app.shell_context_processor
def make_shell_context():
    from auth.models import User
    from marketplace.models import Strategy
    from payments.models import Transaction
    return {
        'db': db,
        'User': User,
        'Strategy': Strategy,
        'Transaction': Transaction
    }

@celery.task
def async_task(task_name, *args, **kwargs):
    """Generic async task handler"""
    if task_name == 'train_model':
        from ai.trainer import AITrainer
        trainer = AITrainer()
        asyncio.run(trainer.train_with_recent_data())
    elif task_name == 'process_payment':
        from payments.services import process_payment_async
        process_payment_async(*args, **kwargs)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)