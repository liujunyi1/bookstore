import sqlite3
import json
import os
import base64
import pymongo
from pymongo import MongoClient

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return base64.b64encode(obj).decode('utf-8')
        return json.JSONEncoder.default(self, obj)


client = MongoClient('mongodb://localhost:27017/')  # 默认连接本地 MongoDB
db = client['bookstore']  # 数据库名称
collection = db['book']  # 集合名称

# 连接到 SQLite 数据库
conn = sqlite3.connect('book.db')
cursor = conn.cursor()

# 查询表中的所有数据
cursor.execute("SELECT * FROM book")
rows = cursor.fetchall()

# 获取表的列名
cursor.execute("PRAGMA table_info(book)")
columns = [column[1] for column in cursor.fetchall()]

# 将数据转换为 JSON 格式
data = []
for row in rows:
    row_data = {}
    for i, column in enumerate(columns):
        row_data[column] = row[i]
    data.append(row_data)
    tags=row_data['tags'].split('\n')
    row_data['tags']=tags
    print(row_data['tags'])
    collection.insert_one(row_data)

# 将数据导出到 JSON 文件
# with open('book_data.json', 'w', encoding='utf-8') as f:
#     json.dump(data, f, indent=4, cls=CustomEncoder,ensure_ascii=False)

# 关闭连接
conn.close()