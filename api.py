import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from article import article

import main

app = Flask(__name__)

CORS(app, resources={
    r"/*": {
        "origins": "http://localhost:3000",
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

@app.route("/<string:company>", methods=['GET'])
def get_stock_data(company):
    articleobj = article(company)
    data = articleobj.get_all_article()
    return jsonify({"Data":data})

@app.route("/start", methods=['GET'])
def start_scraping():
    main.start()
    return None


if __name__ == '__main__':
   app.run(port=8080)