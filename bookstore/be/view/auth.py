from flask import Blueprint
from flask import request
from flask import jsonify
from be.model import user
from be.model.book import searchBook
bp_auth = Blueprint("auth", __name__, url_prefix="/auth")


@bp_auth.route("/login", methods=["POST"])
def login():
    user_id = request.json.get("user_id", "")
    password = request.json.get("password", "")
    terminal = request.json.get("terminal", "")
    u = user.User()
    code, message, token = u.login(
        user_id=user_id, password=password, terminal=terminal
    )
    return jsonify({"message": message, "token": token}), code


@bp_auth.route("/logout", methods=["POST"])
def logout():
    user_id: str = request.json.get("user_id")
    token: str = request.headers.get("token")
    u = user.User()
    code, message = u.logout(user_id=user_id, token=token)
    return jsonify({"message": message}), code


@bp_auth.route("/register", methods=["POST"])
def register():
    user_id = request.json.get("user_id", "")
    password = request.json.get("password", "")
    u = user.User()
    code, message = u.register(user_id=user_id, password=password)
    return jsonify({"message": message}), code


@bp_auth.route("/unregister", methods=["POST"])
def unregister():
    user_id = request.json.get("user_id", "")
    password = request.json.get("password", "")
    u = user.User()
    code, message = u.unregister(user_id=user_id, password=password)
    return jsonify({"message": message}), code


@bp_auth.route("/password", methods=["POST"])
def change_password():
    user_id = request.json.get("user_id", "")
    old_password = request.json.get("oldPassword", "")
    new_password = request.json.get("newPassword", "")
    u = user.User()
    code, message = u.change_password(
        user_id=user_id, old_password=old_password, new_password=new_password
    )
    return jsonify({"message": message}), code


@bp_auth.route("/search_book", methods=["POST"])
def search_book():
    searchbook = searchBook()
    page_no=request.json.get("page_no", 1)
    page_size=request.json.get("page_size", 10)
    reqtags = request.json.get("reqtags", None)
    id=request.json.get("id", None)
    title=request.json.get("title", None)
    isbn=request.json.get("isbn", None)
    author=request.json.get("author", None)
    lowest_price=request.json.get("lowest_price", None)
    highest_price=request.json.get("highest_price", None)
    lowest_pub_year=request.json.get("lowest_pub_year", None)
    highest_pub_year=request.json.get("highest_pub_year", None)
    store_id=request.json.get("store_id", None)
    publisher=request.json.get("publisher", None)
    having_stock=request.json.get("having_stock", None)
    sorted_need=request.json.get("sorted_need", None)
    author_intro=request.json.get("author_intro", None)
    book_intro=request.json.get("book_intro", None)
    code,message,books=searchbook.find_book(page_no,page_size,reqtags,id,title,isbn,author,lowest_price,highest_price,lowest_pub_year,highest_pub_year,store_id,publisher,having_stock,sorted_need,author_intro,book_intro)
    return jsonify({"message": message,"books":books}),code
    
