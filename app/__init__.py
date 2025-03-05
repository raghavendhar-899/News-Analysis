from flask import Flask
# from flask_migrate import Migrate
from flask_cors import CORS
from app.utils.database import get_database as db
from app.api import news

# def create_app(config_class=Config):
def create_app():
    app = Flask(__name__)
    # app.config.from_object(config_class)

    CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
    })

    # Initialize extensions
    # db.init_app(app)
    # Migrate(app, db)

    # Register blueprints
    app.register_blueprint(news.bp)
    # app.register_blueprint(users.bp)

    # Register error handlers
    # from app.exceptions import handlers
    # app.register_error_handler(404, handlers.not_found_error)
    # app.register_error_handler(500, handlers.internal_error)

    return app