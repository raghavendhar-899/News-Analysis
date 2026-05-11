from flask import Blueprint, jsonify, request

from app.repository import token_usage

bp = Blueprint("tokens", __name__, url_prefix="")


@bp.after_request
def _no_store_tokens(resp):
    resp.headers["Cache-Control"] = "no-store"
    return resp


@bp.route("/tokens/usage", methods=["GET"])
def get_usage():
    g = (request.args.get("granularity") or "day").lower()
    limits = {"hour": 48, "day": 31, "month": 24, "year": 10}
    default_limit = limits.get(g, 31)
    try:
        limit = int(request.args.get("limit", default_limit))
    except ValueError:
        limit = default_limit
    limit = max(1, min(limit, 500))
    tz = request.args.get("timezone") or request.args.get("tz")
    data = token_usage.aggregate(g, limit=limit, timezone_name=tz)
    return jsonify(data)


@bp.route("/tokens/totals", methods=["GET"])
def get_totals():
    return jsonify(token_usage.totals_all_time())


@bp.route("/tokens/services", methods=["GET"])
def get_services():
    return jsonify({"services": token_usage.list_services()})
