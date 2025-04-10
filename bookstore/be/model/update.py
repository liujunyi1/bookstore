import sys
sys.path.append(r"C:\Users\19902\Desktop\CDMS.Xuan_ZHOU.2025Spring.DaSE-master\cdms.xuan_zhou.2025spring.dase\bookstore")

import time
import pymongo
import uuid
import json
import logging
from be.model import db_conn
from be.model import error
from be.model import db_conn


class Scanner(db_conn.DBConn):#该类用于扫描订单，将过期订单状态改为canceled，并将库存量和销量更新

    def __init__(self, live_time, scan_interval):
        db_conn.DBConn.__init__(self)
        self.live_time = 10
        self.scan_interval = 10

    def update(self, keep=False):
        tim=0
        while(1):
           time.sleep(self.scan_interval)
           tim+=1
           if tim>=50:
               break
           #找到所有过期的订单，并将状态改为canceled
           cursor=self.conn["new_order"].find({"status":"buy_unpaid","create_time": {"$lt": time.time()-self.live_time}})     
           conn=self.conn   
           for order in cursor:
               order_id=order["order_id"]
               conn["new_order"].update_one({"order_id":order_id},{"$set":{"status":"canceled"}})
               conn['store'].update_many({"store_id": order["store_id"]}, {"$inc": {"stock_level": detail["count"] for detail in conn["order_detail"].find({"order_id": order_id})}})
               conn['store'].update_many({"store_id": order["store_id"]}, {"$inc": {"purchase_count": -detail["count"] for detail in conn["order_detail"].find({"order_id": order_id},)}})
               #conn['store'].update_many({"store_id": order["store_id"]}, {"$dec": {"sales": detail["count"] for detail in conn["order_detail"].find({"order_id": order_id})}})
               #更新库存量和销量
               
# s=Scanner(live_time=10,scan_interval=10)
# s.update()
 