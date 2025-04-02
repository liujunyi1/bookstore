import os
import sqlite3 as sqlite
import pymongo
import random
import base64
import simplejson as json
from pymongo import MongoClient
import sys
#sys.setdefaultencoding('utf-8')

class Book:
    id: str
    title: str
    author: str
    publisher: str
    original_title: str
    translator: str
    pub_year: str
    pages: int
    price: int
    currency_unit: str
    binding: str
    isbn: str
    author_intro: str
    book_intro: str
    content: str
    tags: [str]
    pictures: [bytes]

    def __init__(self):
        self.tags = []
        self.pictures = []


class BookDB:
    def __init__(self):
        # parent_path = os.path.dirname(os.path.dirname(__file__))
        # self.db_s = os.path.join(parent_path, "data/book.db")
        # self.db_l = os.path.join(parent_path, "data/book_lx.db")
        # if large:
        #     self.book_db = self.db_l
        # else:
        #     self.book_db = self.db_s
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['bookstore']
    def get_book_count(self):
        #conn = sqlite.connect(self.book_db)
        
        # cursor = conn.execute("SELECT count(id) FROM book")
        # row = cursor.fetchone()
        # return row[0]
        collection = self.db['book']
        return collection.count_documents({})

    def get_book_info(self, start, size) -> [Book]:
        # books = []
        # conn = sqlite.connect(self.book_db)
        # cursor = conn.execute(
        #     "SELECT id, title, author, "
        #     "publisher, original_title, "
        #     "translator, pub_year, pages, "
        #     "price, currency_unit, binding, "
        #     "isbn, author_intro, book_intro, "
        #     "content, tags, picture FROM book ORDER BY id "
        #     "LIMIT ? OFFSET ?",
        #     (size, start),
        # )
        # for row in cursor:
        #     book = Book()
        #     book.id = row[0]
        #     book.title = row[1]
        #     book.author = row[2]
        #     book.publisher = row[3]
        #     book.original_title = row[4]
        #     book.translator = row[5]
        #     book.pub_year = row[6]
        #     book.pages = row[7]
        #     book.price = row[8]

        #     book.currency_unit = row[9]
        #     book.binding = row[10]
        #     book.isbn = row[11]
        #     book.author_intro = row[12]
        #     book.book_intro = row[13]
        #     book.content = row[14]
        #     tags = row[15]

        #     picture = row[16]

        #     for tag in tags.split("\n"):
        #         if tag.strip() != "":
        #             book.tags.append(tag)
        #     for i in range(0, random.randint(0, 9)):
        #         if picture is not None:
        #             encode_str = base64.b64encode(picture).decode("utf-8")
        #             book.pictures.append(encode_str)
        #     books.append(book)
            # print(tags.decode('utf-8'))

            # print(book.tags, len(book.picture))
            # print(book)
            # print(tags)
        collection = self.db['book']
        cursor = collection.find().sort('_id').skip(start).limit(size)
        books = []
        for row in cursor:
            book = Book()
            book.id = str(row['_id'])
            book.title = row['title']
            book.author = row['author']
            book.publisher = row['publisher']
            book.original_title = row['original_title']
            book.translator = row['translator']
            book.pub_year = row['pub_year']
            book.pages = row['pages']
            book.price = row['price']
            book.currency_unit = row['currency_unit']
            book.binding = row['binding']
            book.isbn = row['isbn']
            book.author_intro = row['author_intro']
            book.book_intro = row['book_intro']
            book.content = row['content']
            book.tags = row['tags']
            book.pictures = row['picture']
            books.append(book)
        return books

# print("---------------------------------")
# book_db = BookDB()
# print(book_db.get_book_count())
# res=book_db.get_book_info(0, 1)
# for book in res:
#     #print(book.id, book.title, book.author, book.publisher, book.original_title, book.translator, book.pub_year, book.pages, book.price, book.currency_unit, book.binding, book.isbn, book.author_intro, book.book_intro, book.content, book.tags, book.pictures)
#     print(book.id,book.title)