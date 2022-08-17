from db.MongoConn import MongoConn


class Station:
    def list_stations(self, page=1):
        mongo_conn = MongoConn()
        client = mongo_conn.conn()

        station_collection = client['station']
        total = station_collection.count_documents({})
        records = station_collection.find({}, {"_id": 0}).skip((page - 1) * 10).limit(10)

        list_station_detail = []
        index = 1
        for station in records:
            station['index'] = index + (page - 1) * 10
            list_station_detail.append(station)
            index += 1
        print(list_station_detail)
        return list_station_detail, total

    def list_station_code(self):
        mongo_conn = MongoConn()
        client = mongo_conn.conn()

        station_collection = client['station']
        records = station_collection.find({}, {"_id": 0, "code": 1, "province": 1})
        list_station_code = []
        for station in records:
            list_station_code.append(station)

        return list_station_code

    def search_station(self, code='', province='', page=1):
        mongo_conn = MongoConn()
        client = mongo_conn.conn()

        station_collection = client['station']

        total = station_collection.count_documents({"code": {'$regex': code}, "province": {'$regex': province}})
        records = station_collection.find({"code": {'$regex': code}, "province": {'$regex': province}},
                                          {"_id": 0}).skip((page - 1) * 10).limit(10)
        list_station_code = []

        index = 1
        for station in records:
            station['index'] = index + (page - 1) * 10
            list_station_code.append(station)
            index += 1

        return list_station_code, total
