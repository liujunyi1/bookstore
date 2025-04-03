from flask import Blueprint
from flask import request
from flask import jsonify
from be.model import seller
import json

bp_seller = Blueprint("seller", __name__, url_prefix="/seller")


@bp_seller.route("/create_store", methods=["POST"])
def seller_create_store():
    user_id: str = request.json.get("user_id")
    store_id: str = request.json.get("store_id")
    s = seller.Seller()
    code, message = s.create_store(user_id, store_id)
    return jsonify({"message": message}), code


@bp_seller.route("/add_book", methods=["POST"])
def seller_add_book():
    user_id: str = request.json.get("user_id")
    store_id: str = request.json.get("store_id")
    book_info: str = request.json.get("book_info")
    stock_level: str = request.json.get("stock_level", 0)

    s = seller.Seller()
    code, message = s.add_book(
        user_id, store_id, book_info.get("id"), json.dumps(book_info), stock_level
    )

    return jsonify({"message": message}), code


@bp_seller.route("/add_stock_level", methods=["POST"])
def add_stock_level():
    user_id: str = request.json.get("user_id")
    store_id: str = request.json.get("store_id")
    book_id: str = request.json.get("book_id")
    add_num: str = request.json.get("add_stock_level", 0)

    s = seller.Seller()
    code, message = s.add_stock_level(user_id, store_id, book_id, add_num)

    return jsonify({"message": message}), code

@bp_seller.route("/sent_order", methods=["POST"])
def sent_order():
    seller_id: str = request.json.get("seller_id")
    store_id: str = request.json.get("store_id")
    order_id: str = request.json.get("order_id")
    s = seller.Seller()
    code, message = s.sent_order(seller_id, store_id, order_id)
    return jsonify({"message": message}), code


@bp_seller.route("/get_order_list", methods=["POST"])
def get_order_list():
    user_id:str=request.json.get("user_id",None)
    store_id:str=request.json.get("store_id")
    seller_id:str=request.json.get("seller_id")
    status:str=request.json.get("status",None)
    order_id:str=request.json.get("order_id",None)
    s = seller.Seller()
    code, message, order_list = s.get_order_list(user_id,seller_id, store_id, status, order_id)
    return jsonify({"message": message, "order_list": order_list}), code

