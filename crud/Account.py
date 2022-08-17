import hashlib


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