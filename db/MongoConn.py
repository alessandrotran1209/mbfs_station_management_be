from pymongo import MongoClient
import pymongo


class MongoConn:
    def conn(self):
        connection_string = "mongodb://vhkt:Vhkt%402022@103.21.148.67:27017/?authMechanism=DEFAULT&authSource=hatang-db"
        client = MongoClient(connection_string)

        return client['hatang-db']
