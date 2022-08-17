from pymongo import MongoClient
import pymongo


class MongoConn:
    def conn(self):
        connection_string = "mongodb://localhost:27017"
        client = MongoClient(connection_string)

        return client['mbfs_work_management']