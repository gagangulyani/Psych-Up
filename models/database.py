from pymongo import MongoClient
from bson import ObjectId


class Database(object):
    """
        Database Class for making transactions with MongoDB

    """
    CURSOR = None

    def __init__(self, DB_NAME='Psych-Up', COLLECTION=None):
        self.client = MongoClient('localhost', 27017)
        self.DB_NAME = DB_NAME
        if COLLECTION:
            self.set_collection(COLLECTION)

    def set_collection(self, COLLECTION):
        Database.CURSOR = self.client[self.DB_NAME][COLLECTION]

    @staticmethod
    def insert_one(dict_):
        return Database.CURSOR.insert_one(dict_).inserted_id

    @staticmethod
    def insert_many(list_of_dict):
        return Database.CURSOR.insert_many(list_of_dict).inserted_ids

    @staticmethod
    def find_one(query):
        return Database.CURSOR.find_one(query)

    @staticmethod
    def find(query={}, to_list=True):
        result = Database.CURSOR.find(query)
        if to_list:
            return list(result)
        return result

    @staticmethod
    def delete_one(query):
        """
            Returns True if record is deleted
            Else False
        """
        if Database.CURSOR.delete_one(query).raw_result['n'] == 1:
            return True
        return False

    @staticmethod
    def delete_many(query):
        """
            Returns True if record is deleted
            Else False
        """
        if Database.CURSOR.delete_many(query).raw_result['n'] > 0:
            return True
        return False

    @staticmethod
    def count_documents(query={}):
        return Database.CURSOR.count_documents(query)

    @staticmethod
    def created_at(_id):
        return _id.generation_time

    @staticmethod
    def update_one(query, update_query):
        Database.CURSOR.update_one(query, update_query)
    
    @staticmethod
    def update_many(query, update_query):
        Database.CURSOR.update_many(query, update_query)

if __name__ == "__main__":
    import pprint

    db = Database()
    db.set_collection('Users')

    # Test Insert Function
    db.insert_one({'name': 'Gagan Deep Singh', 'age': 21,
                   'number_of_wins': 2, 't_score': 750})

    db.insert_many(
        [
            {'name': 'Hardik Soni', 'age': 21, 'number_of_wins': 3, 't_score': 1200},
            {'name': 'Mayank Setia', 'age': 21, 'number_of_wins': 2, 't_score': 900}

        ]
    )

    # Display All Records (in pretified version)
    pprint.pprint(db.find())

    # Updating field of one record
    db.update_one({'name': 'Gagan Deep Singh'}, {'$set': {'age': 22}})
    
    pprint.pprint(db.find())
    
    # Updating field of All Records
    db.update_many({}, {'$set': {'number_of_wins': 0}})
    
    pprint.pprint(db.find())
    
    # Delete All Records
    print("All records Deleted!" if db.delete_many({})
          else "Couldn't Find Any Record To Delete")

    # Display All
    pprint.pprint(db.find() if db.find()
                  else "Couln't find any record to Display!")
