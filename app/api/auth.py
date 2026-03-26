from flask import Blueprint, jsonify, request, make_response

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    # Minimal placeholder implementation. Replace with real auth logic.
    return jsonify({'message': 'login not implemented'}), 501


@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    return jsonify({'message': 'refresh not implemented'}), 501
