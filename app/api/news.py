import json
from flask import Blueprint, Flask, jsonify, request, make_response
from flask_cors import CORS
from app.repository.article import Article
from app.repository.company import Company
from threading import Thread

from app import main


bp = Blueprint('news', __name__, url_prefix='')

    
@bp.route("/start", methods=['GET']) # This route is for starting the scraping process
def start_scraping():
    print("Starting the scraping process")
    main.start()
    return None
    
@bp.route("/test", methods=['GET'])
def test():
    return "Up and running"

@bp.route("/health", methods=['GET'])
def health():
    return make_response('', 200)
