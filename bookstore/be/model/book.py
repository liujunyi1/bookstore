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
        page_no=1,
        page_size=5,
        #foozytitle=None,#搜索关键字
        reqtags=None,#标签搜索,格式为json数组
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
        #order_by_method=None,  # [stock_level, sales, pub_time, price] + [1,-1]  1 means increasingly and -1 means decreasingly
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
        if(title!=None):
            query['title']={"$regex":title, "$options":"i"}
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
                books=self.conn['store'].find(query).skip((page_no-1)*page_size).limit(page_size).sort(sortt)
            else:
                books=self.conn['store'].find(query).skip((page_no-1)*page_size).limit(page_size)    
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

          
        # query="select * from book_info "
        # conditions = " where "
        # fill=list()
        # try:
        #     if (foozytitle != None):
        #         conditions+=" title like %s and"
        #         fill.append(foozytitle+"%")#模糊搜索标题
        #     if (reqtags != None):#标签搜索
        #         conditions+= " tags @> %s and"
        #         fill.append(reqtags)
        #     if (id != None):#图书id搜索
        #         conditions+=" book_id=%s and"
        #         fill.append(id)
        #     if (isbn != None):#图书isbn搜索
        #         conditions+=" isbn=%s and"
        #         fill.append(isbn)
        #     if (author != None):#图书作者搜索
        #         conditions+=" author=%s and"
        #         fill.append(author)
        #     if (lowest_price != None):#图书最低价格搜索
        #         conditions+=" price>=%s and"
        #         fill.append(lowest_price)
        #     if (highest_price != None):#图书最高价格搜索
        #         conditions+=" price<=%s and"
        #         fill.append(highest_price)
        #     if (store_id != None):#图书所属商店搜索
        #         conditions+=" store_id=%s and"
        #         fill.append(store_id)
        #     if (lowest_pub_year != None):#图书最早出版年份搜索
        #         conditions+=" pub_year>=%s and"
        #         fill.append(lowest_pub_year)
        #     if (highest_pub_year != None):#图书最晚出版年份搜索
        #         conditions+=" pub_year<%s and"
        #         fill.append(str(int(highest_pub_year)+1))
        #     if (publisher != None):#图书出版社搜索
        #         conditions+=" publisher=%s and"
        #         fill.append(publisher)
        #     if (translator != None):#图书译者搜索
        #         conditions+=" translator=%s and"
        #         fill.append(translator)
        #     if (binding != None):#图书装帧搜索
        #         conditions+=" binding=%s and"
        #         fill.append(binding)
        #     if (having_stock == True):#图书库存不为0搜索
        #         conditions+=" stock_level>0 and"

        #     if(len(conditions)>7):#去掉最后的and
        #         conditions=conditions[:-3]
        #     else:
        #         conditions=" "#条件为空，返回全部图书
        #     if (order_by_method != None):#排序
        #         if (order_by_method[0] not in self.order_by_conditions or
        #             (order_by_method[1] != 1 and order_by_method[1] != -1)):
        #             return 522, error.error_illegal_order_condition(
        #                 str(order_by_method[0] + ' ' + order_by_method[1])), ""
        #         conditions+=" order by "+"\""+order_by_method[0]+"\" "
        #         if(order_by_method[1]==1):
        #             conditions+="asc "
        #         else:
        #             conditions+="desc "
            
        #     conn=self.get_conn()#获取数据库连接
        #     cur=conn.cursor()#创建游标
        #     cur.execute(query+conditions+" limit "+str(page_size)+" offset "+str(page_no*page_size),fill)#
        #     res=cur.fetchall()
        #     for row in res:#遍历结果集
        #         book=dict()
        #         book['book_id']=row[0]
        #         book['store_id']=row[1]
        #         book['price']=row[2]
        #         book['stock_level']=row[3]
        #         book['sales']=row[4]
        #         book['title']=row[5]
        #         book['author']=row[6]
        #         book['tags']=row[7]

        #         book['publisher']=row[8]
        #         book['original_title']=row[9]
        #         book['translator']=row[10]
        #         book['pub_year']=row[11]
        #         book['pages']=row[12]
        #         book['currency_unit']=row[13]
        #         book['binding']=row[14]
        #         book['isbn']=row[15]
        #         book['author_intro']=row[16]
        #         book['book_intro']=row[17]
        #         book['content']=row[18]
        #         book['picture']=row[19]
        #         books.append(json.dumps(book))#json.dumps()用于将字典转换为json格式
        # except psycopg2.Error as e:
        #     logging.info("528, {}".format(str(e)))
        #     return 528, "{}".format(str(e)), ""
        # except BaseException as e:
        #     logging.info("530, {}".format(str(e)))
        #     return 530, "{}".format(str(e)), ""
        
        #return 200, "ok", books#返回搜索结果，包括图书信息，错误信息，以及分页信息

# search=searchBook()
# cursor=search.conn['store'].find({'tags': {'$all': ['三毛', '撒哈拉的故事', '旅行']}})
#res=search.find_book(reqtags=['三毛','撒哈拉的故事','旅行'])

# search=searchBook()
# #cursor=searchBook.find_book(reqtags=['三毛'],lowest_price=1500,highest_price=3000) 
# cursor=search.find_book() 

