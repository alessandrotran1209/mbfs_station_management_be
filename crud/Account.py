import hashlib

from db.MongoConn import MongoConn


class Account:

    def authenticate(self, client, username, password):
        user_collection = client['user']
        user = user_collection.find({"username" : username})
        for record in user:
            hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
            if hashed_password == record['password']:
                print('Password matched')
                return True
        return False

    def get_user(self, username):
        mongo_conn = MongoConn()
        client = mongo_conn.conn()
        user_collection = client['user']
        user = user_collection.find({"username": username})
        for record in user:
            u = record
            return u

    def insert_user(self, data):
        try:
            mongo_conn = MongoConn()
            client = mongo_conn.conn()
            user_collection = client['user']

            user_collection.insert_one(data)
        except Exception as e:
            raise Exception(e)
        return True