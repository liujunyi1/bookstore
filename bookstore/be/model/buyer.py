import sys
sys.path.append(r"C:\Users\19902\Desktop\CDMS.Xuan_ZHOU.2025Spring.DaSE-master\cdms.xuan_zhou.2025spring.dase\bookstore")

import time
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
                    "store_id": store_id,
                    "price": price,
                } 
                self.conn["order_detail"].insert_one(order_detail)

            order = {"order_id": uid, "user_id": user_id, "store_id": store_id, "status": "buy_unpaid", "create_time": time.time()}
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
            
            pass_time = time.time() - order["create_time"]
            if pass_time > 3600:
                return error.error_invalid_order_status(order_id)

            if order["status"] != "buy_unpaid":
                return error.error_invalid_order_status(order_id)
            
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
            #conn["new_order"].delete_one({"order_id": order_id})
            conn["new_order"].update_one({"order_id": order_id}, {"$set": {"status": "paid_unsent"}})
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
     
    def cancel_order(self, user_id: str, password: str, order_id: str) -> (int, str):
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

            if order["status"] == "buy_unpaid":
                conn["new_order"].update_one({"order_id": order_id}, {"$set": {"status": "cancelled"}})
            elif order["status"] == "paid_unsent" or "sent_unreceived" or "received":
                conn["new_order"].update_one({"order_id": order_id}, {"$set": {"status": "cancelled"}})
                price = sum(detail["price"] * detail["count"] for detail in conn["order_detail"].find({"order_id": order_id}))
                conn["user"].update_one({"user_id": buyer["user_id"]}, {"$inc": {"balance": price}})
                seller_id = conn["user_store"].find_one({"store_id": order["store_id"]})["user_id"]
                conn["user"].update_one({"user_id": seller_id}, {"$inc": {"balance": -price}})
                conn['store'].update_many({"store_id": order["store_id"]}, {"$inc": {"stock_level": detail["count"] for detail in conn["order_detail"].find({"order_id": order_id})}})
            
        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"
                #conn["order_detail"].delete_many({"order_id": order_id})
        

        
        
        def received_order(self, user_id: str,store_id: str, order_id: str) -> (int, str):
            conn = self.conn
            try:
                order = conn["new_order"].find_one({"order_id": order_id})
                if not order:
                    return error.error_invalid_order_id(order_id)
                if order["user_id"] != user_id:
                    return error.error_authorization_fail()  
                if order["store_id"] != store_id:
                    return error.error_authorization_fail()
                if order["status"] != "sent_unreceived":
                    return error.error_invalid_order_status(order_id)
                
                conn["new_order"].update_one({"order_id": order_id}, {"$set": {"status": "received"}})
            except pymongo.errors.PyMongoError as e:
                return 528, "{}".format(str(e))
            except BaseException as e:
                return 530, "{}".format(str(e))
            return 200, "ok"
        
        def get_order_list(self, user_id: str) -> (int, str, list):
            conn = self.conn
            try:
                orders = list(conn["new_order"].find({"user_id": user_id}))
                if not orders:
                    return error.error_non_exist_order_list(user_id)
                order_list = []
                for order in orders:
                    order_id = order["order_id"]
                    order_detail = list(conn["order_detail"].find({"order_id": order_id}))
                    order_info = {"order_id": order_id, "status": order["status"]}
                    ##检查当前时间和订单发起时间的时间差
                    pass_time = time.time() - order["create_time"]
                    if pass_time > 3600:
                        order_info["status"] = "cancelled"
                    for detail in order_detail:
                        #book_info = conn["store"].find_one({"store_id": detail["store_id"], "book_id": detail["book_id"]})
                        #book_info_json = json.loads(book_info["book_info"])
                        #book_info_json["count"] = detail["count"]
                        #order_info[detail["book_id"]] = book_info_json
                        order_info["book_id"] = detail["book_id"]
                        order_info["count"] = detail["count"]
                        order_info["price"] = detail["price"]
                        order_info["store_id"] = detail["store_id"] 
                        
                    order_list.append(order_info)
            except pymongo.errors.PyMongoError as e:
                return 528, "{}".format(str(e)), []
            except BaseException as e:
                return 530, "{}".format(str(e)), []
            return 200, "ok", order_list
        
         
        

  
 