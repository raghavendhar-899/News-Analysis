import json
from flask import Blueprint, Flask, jsonify, request, make_response
from flask_cors import CORS
from app.repository.article import Article
from app.repository.company import Company
from threading import Thread

from app import main


bp = Blueprint('news', __name__, url_prefix='')

    
@bp.route("/start", methods=["POST"])
def start_scraping():
    # Use POST to avoid browsers triggering this via prefetch/speculative loading.
    t = Thread(target=main.start, daemon=True)
    t.start()
    return jsonify({"status": "started", "thread": t.name}), 202


@bp.route("/start", methods=["GET"])
def start_scraping_get():
    # Some browsers (notably Safari) may prefetch GETs as you type.
    # Keep GET side-effect free.
    return (
        jsonify(
            {
                "error": "Use POST /start to begin scraping",
                "hint": "Example: curl -X POST http://127.0.0.1:8081/start",
            }
        ),
        405,
    )
    
@bp.route("/test", methods=['GET'])
def test():
    return "Up and running"

@bp.route("/health", methods=['GET'])
def health():
    return make_response('', 200)
