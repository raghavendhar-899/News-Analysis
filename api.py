import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from article import article

import main
from company import company

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
    sorted_articles = sorted(data, key=lambda x: x['date'], reverse=True)
    print(data[:10])
    return jsonify({"Data":sorted_articles})

@app.route("/start", methods=['GET'])
def start_scraping():
    main.start()
    return None

@app.route("/newcompany", methods=['POST'])
def new_company():
    data = request.json
    name = data.get('name')
    locations = data.get('locations')
    score = data.get('score')
    primary_location = data.get('primary_location')
    companyobj = company()
    if companyobj.find_company(name):
        return 'Company already exist'
    companyobj.insert_company(name, locations, score, primary_location)
    return 'Received POST request'


if __name__ == '__main__':
   app.run(port=8080)