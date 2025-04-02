import sys
sys.path.append(r"C:\Users\19902\Desktop\CDMS.Xuan_ZHOU.2025Spring.DaSE-master\cdms.xuan_zhou.2025spring.dase\bookstore")


import pymongo
import uuid
import json
import logging
from be.model import db_conn
from be.model import error


class Buyer(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def new_order(
        self, user_id: str, store_id: str, id_and_count: [(str, int)]
    ) -> (int, str, str):
        order_id = ""
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id,)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + (order_id,)
            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))
            
            

            for book_id, count in id_and_count:
                cursor = self.conn["store"].find_one({"store_id": store_id, "book_id": book_id})
                if not cursor:
                    return error.error_non_exist_book_id(book_id) + (order_id,)

                stock_level = cursor["stock_level"]
                # book_info = cursor["book_info"]
                # book_info_json = json.loads(book_info)
                # price = book_info_json.get("price")
                price=cursor['price']

                if stock_level < count:
                    return error.error_stock_level_low(book_id) + (order_id,)

                books = {"book_id": book_id, "store_id": store_id, "stock_level": {"$gte": count}}
                update = {"$inc": {"stock_level": -count}}
                result = self.conn["store"].update_one(books, update)
                if result.modified_count == 0:
                    return error.error_stock_level_low(book_id) + (order_id,)

                order_detail = {
                    "order_id": uid,
                    "book_id": book_id,
                    "count": count,
                    "price": price,
                    "status":"buy_unpaid"
                }
                self.conn["order_detail"].insert_one(order_detail)

            order = {"order_id": uid, "user_id": user_id, "store_id": store_id}
            self.conn["new_order"].insert_one(order)
            #self.conn.commit()
            order_id = uid
        except pymongo.errors.PyMongoError as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""

        return 200, "ok", order_id

    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        conn = self.conn
        try:
            order = conn["new_order"].find_one({"order_id": order_id})
            if not order:
                return error.error_invalid_order_id(order_id)

            
            if order["user_id"] != user_id:
                return error.error_authorization_fail()

            buyer = conn["user"].find_one({"user_id": user_id})
            if not buyer:
                return error.error_non_exist_user_id(user_id)
            if password != buyer["password"]:
                return error.error_authorization_fail()
            
            price = sum(detail["price"] * detail["count"] for detail in conn["order_detail"].find({"order_id": order_id}))
            if buyer["balance"] < price:
                return error.error_not_sufficient_funds(order_id)

            change = conn["user"].update_one({"user_id": user_id, "balance": {"$gte": price}}, {"$inc": {"balance": -price}})
            if change.modified_count == 0:
                return error.error_not_sufficient_funds(order_id)
            seller_id = conn["user_store"].find_one({"store_id": order["store_id"]})["user_id"]
            change = conn["user"].update_one({"user_id": seller_id}, {"$inc": {"balance": price}})
            if change.modified_count == 0:
                return error.error_non_exist_user_id(seller_id)
            conn["new_order"].delete_one({"order_id": order_id})
            #conn.commit()

        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))

        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def add_funds(self, user_id, password, add_value) -> (int, str):
        conn=self.conn
        try:
            user = conn["user"].find_one({"user_id": user_id})
            if not user or user["password"] != password:
                return error.error_authorization_fail()

            result = conn["user"].update_one({"user_id": user_id}, {"$inc": {"balance": add_value}})
            if result.modified_count == 0:
                return error.error_non_exist_user_id(user_id)
            
            #self.conn.commit()
        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

 