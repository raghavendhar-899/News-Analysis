from flask import Config, Flask
# from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.utils.database import get_database as db
from app.api import auth, news, users
from flask_jwt_extended import JWTManager as JWTExtended

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


    # Register blueprints
    app.register_blueprint(news.bp)
    app.register_blueprint(auth.auth_bp, url_prefix='/auth')
    app.register_blueprint(users.users_bp)
    # app.register_blueprint(users.bp)

    # Register error handlers
    # from app.exceptions import handlers
    # app.register_error_handler(404, handlers.not_found_error)
    # app.register_error_handler(500, handlers.internal_error)

    return app