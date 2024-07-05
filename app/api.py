import json
from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from article import article
from company import company
from threading import Thread

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

@app.route("/<string:companyname>", methods=['GET'])
def get_stock_data(companyname):
    articleobj = article(companyname)
    companyobj = company()
    data = articleobj.get_all_article()
    if not data:
        return make_response('', 404)
    sorted_articles = sorted(data, key=lambda x: x['date'], reverse=True)
    score = companyobj.find_company(companyname)['score']
    return jsonify({"Data":sorted_articles, "score":score})

@app.route("/start", methods=['GET'])
def start_scraping():
    main.start()
    return None

@app.route("/newcompany", methods=['POST'])
def new_company():
    data = request.json
    name = data.get('name')
    ticker = data.get('ticker')
    primary_location = data.get('location')
    companyobj = company()
    if companyobj.find_company(name):
        return make_response('', 409)  # 409 Conflict
    companyobj.insert_company(name,ticker, "", 0, primary_location)
    # Start a new thread to execute main.new_company asynchronously
    # This will allow the response to be returned immediately
    thread = Thread(target=main.new_company, args=(name, primary_location))
    thread.start()
    return make_response('', 201)  # 201 Created

@app.route('/suggestions', methods=['GET'])
def get_suggestions():
    query = request.args.get('query', '').strip()
    companyobj = company()
    if query:
        suggestions = companyobj.get_company_name_suggestions(query)
        print('suggestion',suggestions)
        suggestions=jsonify(suggestions)
        return suggestions
    else:
        return jsonify([])


if __name__ == '__main__':
   app.run(port=8080)