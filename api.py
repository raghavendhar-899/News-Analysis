import json
from flask import Flask, jsonify, request
from flask_cors import CORS

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

@app.route("/<string:company>/<string:country>", methods=['GET'])
def get_stock_data(company,country):
    data = main.main(company,country)
    return jsonify({"Data":data})


if __name__ == '__main__':
   app.run(port=8080)