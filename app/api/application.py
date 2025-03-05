import json
from flask import Blueprint, Flask, jsonify, request, make_response
from flask_cors import CORS
from app.repository.article import article
from app.repository.company import company
from threading import Thread

from app.services import main


# application = Flask(__name__)

# app = application

bp = Blueprint('users', __name__, url_prefix='')



@bp.route("/<string:companyname>", methods=['GET']) # This route is for getting the News data of a company
def get_stock_data(companyname):
    print(companyname)
    articleobj = article(companyname)
    companyobj = company()
    data = articleobj.get_all_article()
    if not data:
        return make_response('', 404)
    score = companyobj.find_company(companyname)['score']
    return jsonify({"Data":data, "score":score})


@bp.route("/newcompany", methods=['POST']) # This route is for adding a new company
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

@bp.route('/suggestions', methods=['GET']) # This route is for the search suggestions
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


# if __name__ == '__main__':
# #    app.run(port=8080)
#     app.run(host='0.0.0.0', port=8080)