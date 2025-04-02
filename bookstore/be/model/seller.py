import sys
sys.path.append(r"C:\Users\19902\Desktop\CDMS.Xuan_ZHOU.2025Spring.DaSE-master\cdms.xuan_zhou.2025spring.dase\bookstore")
import json
import pymongo
import time
from be.model import error
from be.model import db_conn


class Seller(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def add_book(
        self,
        user_id: str,
        store_id: str,
        book_id: str,
        book_json_str: str,
        stock_level: int,
    ):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if self.book_id_exist(store_id, book_id):
                return error.error_exist_book_id(book_id)
            book_json_str=json.loads(book_json_str) 
            doc={
                'store_id': store_id,
                'book_id': book_id,
                'book_info': book_json_str,
                'title': book_json_str['title'],
                'author': book_json_str['author'],
                'publisher': book_json_str['publisher'],
                'original_title': book_json_str['original_title'],
                'price': book_json_str['price'],
                'currency_unit': book_json_str['currency_unit'],
                'binding': book_json_str['binding'],
                'isbn': book_json_str['isbn'],
                'author_intro': book_json_str['author_intro'],
                'book_intro': book_json_str['book_intro'],
                'content': book_json_str['content'],
                'tags': book_json_str['tags'],
                'stock_level': stock_level
            }
            self.conn['store'].insert_one(doc)
            #print(doc)
            #self.conn.commit()
        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def add_stock_level(
        self, user_id: str, store_id: str, book_id: str, add_stock_level: int
    ):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if not self.book_id_exist(store_id, book_id):
                return error.error_non_exist_book_id(book_id)

            self.conn['store'].update_one(
                {'store_id': store_id, 'book_id': book_id},
                {'$inc': {'stock_level': add_stock_level}},
            )
            #self.conn.commit()
        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def create_store(self, user_id: str, store_id: str) -> (int, str):
        try:
            if not self.user_id_exist(user_id):
                #print("user_id not exist")
                return error.error_non_exist_user_id(user_id)
            if self.store_id_exist(store_id):
                #print("store_id exist")
                return error.error_exist_store_id(store_id)
            #print("-----------------------------")
            user_store_doc = {
                'user_id': user_id,
                'store_id': store_id
            }
            self.conn['user_store'].insert_one(user_store_doc)
            #print(user_store_doc)
            #self.conn.commit()
        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"
    
    def sent_order(self, user_id: str, store_id: str, order_id: str) -> (int, str):
            conn = self.conn
            try:
                order = conn["new_order"].find_one({"order_id": order_id})
                if not order:
                    return error.error_invalid_order_id(order_id)
                if order["user_id"] != user_id:
                    return error.error_authorization_fail()
                if order["store_id"] != store_id:
                    return error.error_authorization_fail()
                if order["status"] != "paid_unsent":
                    return error.error_invalid_order_status(order_id)
                
                conn["new_order"].update_one({"order_id": order_id}, {"$set": {"status": "sent_unreceived"}})
            except pymongo.errors.PyMongoError as e:
                return 528, "{}".format(str(e))
            except BaseException as e:
                return 530, "{}".format(str(e))
            return 200, "ok"
    
    def get_store_order_list(self, store_id: str) -> (int, str, list):
            conn = self.conn
            try:
                orders = list(conn["new_order"].find({"store_id": store_id}))
                if not orders:
                    return error.error_non_exist_order_list(store_id)
                order_list = []
                for order in orders:
                    order_id = order["order_id"]
                    order_detail = list(conn["order_detail"].find({"order_id": order_id}))
                    order_info = {"order_id": order_id, "status": order["status"]}
                    pass_time = time.time() - order["create_time"]
                    if pass_time > 3600:
                        order_info["status"] = "cancelled"
                    for detail in order_detail:
                        # book_info = conn["store"].find_one({"store_id": detail["store_id"], "book_id": detail["book_id"]})
                        # book_info_json = json.loads(book_info["book_info"])
                        # book_info_json["count"] = detail["count"]
                        # order_info[detail["book_id"]] = book_info_json
                        order_info["book_id"] = detail["book_id"]
                        order_info["count"] = detail["count"]
                        order_info["price"] = detail["price"]
                        order_info["user_id"] = order["user_id"]
                    order_list.append(order_info)
            except pymongo.errors.PyMongoError as e:
                return 528, "{}".format(str(e)), []
            except BaseException as e:
                return 530, "{}".format(str(e)), []
            return 200, "ok", order_list
    
     

#seller=Seller()
#seller.create_store('user1', 'store1')
#seller.conn['user_store'].insert_one({'user_id':'user2','store_id':'store2'})
#seller.create_store('user1', 'store1')
#seller.create_store('user1', 'store1')
#seller.add_book('user1', 'store1', 'book1', 'book_info1', 10)
#seller.add_stock_level('user1', 'store1', 'book1', 10)