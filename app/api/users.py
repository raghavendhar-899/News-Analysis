from flask import Blueprint, jsonify

users_bp = Blueprint('users', __name__)


@users_bp.route('/users', methods=['GET'])
def list_users():
    # Placeholder implementation. Replace with real user listing logic.
    return jsonify([])
