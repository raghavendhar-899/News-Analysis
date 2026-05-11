from flask import Config, Flask
# from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.utils.database import get_database as db
from app.api import auth, news, tokens, users
from flask_jwt_extended import JWTManager as JWTExtended
from app.utils.logger import configure_logging
import os
import urllib3
from functools import partial

# def create_app(config_class=Config):
def create_app():
    # configure logging as early as possible for consistent output
    configure_logging()

    # Increase urllib3 connection pool for localhost-heavy workloads (e.g. local model servers).
    # urllib3 defaults maxsize=1 which can trigger:
    # "Connection pool is full, discarding connection: localhost. Connection pool size: 1"
    try:
        maxsize = int(os.getenv("URLLIB3_POOL_MAXSIZE", "20"))
        num_pools = int(os.getenv("URLLIB3_NUM_POOLS", str(maxsize)))
        if maxsize > 1:
            urllib3.PoolManager = partial(urllib3.PoolManager, num_pools=num_pools, maxsize=maxsize)
            urllib3.ProxyManager = partial(urllib3.ProxyManager, num_pools=num_pools, maxsize=maxsize)
    except Exception:
        # If urllib3 isn't available or monkeypatching fails, proceed without it.
        pass

    app = Flask(__name__)
    # app.config.from_object(config_class)
    CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS", "HEAD"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
    })


    # Register blueprints
    app.register_blueprint(news.bp)
    app.register_blueprint(tokens.bp)
    app.register_blueprint(auth.auth_bp, url_prefix='/auth')
    app.register_blueprint(users.users_bp)
    # app.register_blueprint(users.bp)

    # Register error handlers
    # from app.exceptions import handlers
    # app.register_error_handler(404, handlers.not_found_error)
    # app.register_error_handler(500, handlers.internal_error)

    return app