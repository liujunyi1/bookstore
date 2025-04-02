import requests
from urllib.parse import urljoin


class Auth:
    def __init__(self, url_prefix):
        self.url_prefix = urljoin(url_prefix, "auth/")

    def login(self, user_id: str, password: str, terminal: str) -> (int, str):
        json = {"user_id": user_id, "password": password, "terminal": terminal}
        url = urljoin(self.url_prefix, "login")
        r = requests.post(url, json=json)
        return r.status_code, r.json().get("token")

    def register(self, user_id: str, password: str) -> int:
        json = {"user_id": user_id, "password": password}
        url = urljoin(self.url_prefix, "register")
        r = requests.post(url, json=json)
        return r.status_code

    def password(self, user_id: str, old_password: str, new_password: str) -> int:
        json = {
            "user_id": user_id,
            "oldPassword": old_password,
            "newPassword": new_password,
        }
        url = urljoin(self.url_prefix, "password")
        r = requests.post(url, json=json)
        return r.status_code

    def logout(self, user_id: str, token: str) -> int:
        json = {"user_id": user_id}
        headers = {"token": token}
        url = urljoin(self.url_prefix, "logout")
        r = requests.post(url, headers=headers, json=json)
        return r.status_code

    def unregister(self, user_id: str, password: str) -> int:
        json = {"user_id": user_id, "password": password}
        url = urljoin(self.url_prefix, "unregister")
        r = requests.post(url, json=json)
        return r.status_code
    
    def seacher(
        self,
        page_no=1,
        page_size=5, 
        reqtags=None,#标签搜索,格式为一个列表
        id=None,
        title=None,
        isbn=None,
        author=None,
        lowest_price=None,
        highest_price=None,
        lowest_pub_year=None,
        highest_pub_year=None,
        store_id=None,
        publisher=None,
        translator=None,
        binding=None,
        having_stock=None,
        sort_need=None,#结果排序要求，格式给一个列表，如[["price",1],["stock",1]]
        author_intro=None,
        book_intro=None
    ):
        
        json = {
            "page_no": page_no,
            "page_size": page_size, 
            "reqtags": reqtags,
            "id": id,
            "title": title,
            "isbn": isbn,
            "author": author,
            "lowest_price": lowest_price,
            "highest_price": highest_price,
            "lowest_pub_year": lowest_pub_year,
            "highest_pub_year": highest_pub_year,
            "store_id": store_id,
            "publisher": publisher,
            "translator": translator,
            "binding": binding, 
            "having_stock": having_stock,
            "sort_need": sort_need,
            "author_intro": author_intro,
            "book_intro": book_intro
        }
        url = urljoin(self.url_prefix, "search")
        r = requests.post(url, json=json)
        return r.status_code, r.json()  