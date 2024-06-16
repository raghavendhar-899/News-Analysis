import json
from flask import Flask, jsonify, request

import main

app = Flask(__name__)

@app.route("/<string:company>/<string:country>", methods=['GET'])
def get_stock_data(company,country):
    data = main.main(company,country)
    return jsonify({"Data":data})


if __name__ == '__main__':
   app.run(port=8080)