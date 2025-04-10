import logging
import os
import pymongo
import threading
from pymongo import MongoClient

class Store:
    client = None
    database = None

    def __init__(self):
        self.client = pymongo.MongoClient('mongodb://localhost:27017')
        self.database = self.client['bookstore']
        self.init_tables()

    def init_tables2(self):
        try:
            
            #self.database["user"].create_index([("user_id", pymongo.ASCENDING)])
            
            
            ############################
            self.database["new_order"].create_index("order_id", unique=True)
            self.database["new_order"].create_index(("status",1),("create_time",1))
            ############################
            self.database["order_detail"].create_index(("order_id",1))
            ############################
            self.database["user"].create_index("user_id", unique=True)
            ############################
            self.database["user_store"].create_index([("store_id", 1),("user_id", 1)], unique=True)
            ############################
            self.database["store"].create_index("store_id","book_id" ,unique=True)
            #self.database["new_order_detail"].create_index([("order_id", 1), ("book_id", 1)], unique=True)
             

        except Exception as e:
            logging.error(f"Error initializing collections: {e}")


    def init_tables(self):
        try:
            self.database["user"].create_index("user_id", unique=True)
            #self.database["user"].create_index([("user_id", pymongo.ASCENDING)])
            self.database["user_store"].create_index([("user_id", 1), ("store_id", 1)], unique=True)
            self.database["store"].create_index([("store_id", 1), ("book_id", 1)], unique=True)
            self.database["new_order"].create_index("order_id", unique=True)
            self.database["new_order_detail"].create_index([("order_id", 1), ("book_id", 1)], unique=True)
        except Exception as e:
            logging.error(f"Error initializing collections: {e}")
    def get_db_conn(self):
        return self.database


database_instance: Store = None
# global variable for database sync
init_completed_event = threading.Event()


def init_database():
    return Store()


def get_db_conn():
    global database_instance
    #return database_instance.get_db_conn() if database_instance else init_database().get_db_conn()
    if not database_instance:
        database_instance = init_database()
    return database_instance.get_db_conn()
