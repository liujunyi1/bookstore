import pymongo
import psycopg2
import json
import logging
import pymongo.errors
import sys
sys.path.append(r"C:\Users\19902\Desktop\CDMS.Xuan_ZHOU.2025Spring.DaSE-master\cdms.xuan_zhou.2025spring.dase\bookstore")
from be.model import db_conn
from be.model import error


class searchBook(db_conn.DBConn):

    def __init__(self):
        db_conn.DBConn.__init__(self)
        self.order_by_conditions = [
            'stock_level', 'sales', 'pub_year', 'price'
        ]#排序条件，可选值为'stock_level','sales', 'pub_year', 'price'

    def find_book(
        self,
        page_no=None,
        page_size=None,
        foozytitle=None,#搜索关键字
        reqtags=None,#标签搜索,格式为json数组
        id=None,
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
        order_by_method=None,  # [stock_level, sales, pub_time, price] + [1,-1]  1 means increasingly and -1 means decreasingly
        having_stock=None,
        sort_need=None,
        author_intro=None,
        book_intro=None
    ):#搜索图书，返回搜索结果，包括图书信息，错误信息，以及分页信息
        # books = list()#搜索结果
        result=list()
        query={} 
        sortt=list()
        if(id!=None):
            query['book_id']=id
        if(reqtags!=None):
            query['tags']={"$all":reqtags}
        if(isbn!=None):
            query['isbn']=isbn
        if(author!=None):
            query['author']=author
        if(lowest_price!=None):
            query['price']={"$gte":lowest_price}
        if(highest_price!=None):
            query['price']={"$lte":highest_price}
        if lowest_price!=None and highest_price !=None:
            query['price']={
                "$gte":lowest_price,
                "$lte":highest_price
            }
        if(lowest_pub_year!=None):
            query['pub_year']={"$gte":lowest_pub_year}
        if(highest_pub_year!=None):
            query['pub_year']={"$lte":highest_pub_year}
        if(lowest_pub_year!=None and highest_pub_year!=None):
            query['pub_year']={
                "$gte":lowest_pub_year,
                "$lte":highest_pub_year
            }
        if(publisher!=None):
            query['publisher']=publisher
        if(translator!=None):
            query['translator']=translator
        if(binding!=None):
            query['binding']=binding
        if(having_stock!=None):
            query['stock_level']={'$gt':0}
        if(store_id!=None):
            query['store_id']=store_id
        if(book_intro!=None):
            query['book_intro']={
                "$regex":book_intro,
                "$options":"i"
            }
        if(author_intro!=None):
            query['author_intro']={
                "$regex":author_intro,
                "$options":"i"
            }
        if sort_need!= None:
            for sort_critea in sort_need:
                sortt.append((sort_critea[0],sort_critea[1]))
        #print(query) 
        try:
            #books = self.db.book_info.find(query).skip((page_no-1)*page_size).limit(page_size)
            books=list()
            if sort_need:
                books=self.conn['store'].find(query).sort(sortt)
            else:
                books=self.conn['store'].find(query)
            for book in books:
                book["_id"]=None
                print(book)
                result.append(json.dumps(book))
        except pymongo.errors.PyMongoError as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""
        return 200, "ok", result#返回搜索结果，包括图书信息，错误信息，以及分页信息

          
         

# search=searchBook()
# cursor=search.conn['store'].find({'tags': {'$all': ['三毛', '撒哈拉的故事', '旅行']}})
#res=search.find_book(reqtags=['三毛','撒哈拉的故事','旅行'])

search=searchBook()
#cursor=searchBook.find_book(reqtags=['三毛'],lowest_price=1500,highest_price=3000) 
cursor=search.find_book() 

