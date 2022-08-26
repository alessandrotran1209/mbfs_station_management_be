from pymongo import MongoClient
import pymongo


class MongoConn:
    def conn(self):
        connection_string = "mongodb+srv://admin:Xls5ZJ4JnmzP18YA@cluster0.u4qqauu.mongodb.net/test"
        client = MongoClient(connection_string)

        return client['hatang-db']