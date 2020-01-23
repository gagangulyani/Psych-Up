from pymongo import MongoClient


class Database(object):
    """
        Database Class for making transactions with MongoDB

    """
    CURSOR = None

    def __init__(self, DB_NAME='Knowledge-Checker'):
        self.client = MongoClient('localhost', 27017)
        self.DB_NAME = DB_NAME

    def set_collection(self, COLLECTION):
        Database.CURSOR = self.client[self.DB_NAME][COLLECTION]

    def insert_one(self, dict_):
        return Database.CURSOR.insert_one(dict_).inserted_id

    def insert_many(self, list_of_dict):
        return Database.CURSOR.insert_many(list_of_dict).inserted_ids

    def find_one(self, query):
        return Database.CURSOR.find_one(query)

    def find(self, query = {}, to_list=True):
        result = Database.CURSOR.find(query)
        if to_list:
            return list(result)
        return result

    def delete_one(self, query):
        return Database.CURSOR.delete_one(query)

    def delete_many(self, query):
        return Database.CURSOR.delete_many(query)

    def count_documents(self, query={}):
        return Database.CURSOR.count_documents(query)


if __name__ == "__main__":
    db = Database()
    db.set_collection('Users')

    print(db.find())
    print(db.delete_many({}))
    print(db.find())
