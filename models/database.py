from pymongo import MongoClient
from bson import ObjectId


class Database(object):
    """
        Database Class for making transactions with MongoDB

    """
    CURSOR = None
    COLLECTION = None

    def __init__(self, DB_NAME='Psych-Up'):
        self.client = MongoClient('localhost', 27017)
        self.DB_NAME = DB_NAME
        Database.CURSOR = self.client[DB_NAME]

    @staticmethod
    def insert_one(COLLECTION, dict_):
        return Database.CURSOR[COLLECTION].insert_one(dict_).inserted_id

    @staticmethod
    def insert_many(COLLECTION, list_of_dict):
        return Database.CURSOR[COLLECTION].insert_many(list_of_dict).inserted_ids

    @staticmethod
    def find_one(COLLECTION, query):
        return Database.CURSOR[COLLECTION].find_one(query)

    @staticmethod
    def find(COLLECTION, query={}, to_list=True, sort={}, limit=1000):
        if not sort:
            result = Database.CURSOR[COLLECTION].find(query, limit=limit)
        else:
            result = Database.CURSOR[COLLECTION].find(
                query, limit=limit).sort(sort)

        if to_list:
            return list(result)
        return result

    @staticmethod
    def delete_one(COLLECTION, query):
        """
            Returns True if record is deleted
            Else False
        """
        if Database.CURSOR[COLLECTION].delete_one(query).raw_result['n'] == 1:
            return True
        return False

    @staticmethod
    def delete_many(COLLECTION, query):
        """
            Returns True if record is deleted
            Else False
        """
        if Database.CURSOR[COLLECTION].delete_many(query).raw_result['n'] > 0:
            return True
        return False

    @staticmethod
    def count_documents(COLLECTION, query={}):
        return Database.CURSOR[COLLECTION].count_documents(query)

    @staticmethod
    def created_at(COLLECTION, _id):
        return _id.generation_time

    @staticmethod
    def update_one(COLLECTION, query, update_query):
        Database.CURSOR[COLLECTION].update_one(query, update_query)

    @staticmethod
    def update_many(COLLECTION, query, update_query):
        Database.CURSOR[COLLECTION].update_many(query, update_query)
