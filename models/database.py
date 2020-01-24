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

    def find(self, query={}, to_list=True):
        result = Database.CURSOR.find(query)
        if to_list:
            return list(result)
        return result

    def delete_one(self, query):
        """
            Returns True if record is deleted
            Else False
        """
        if Database.CURSOR.delete_one(query).raw_result['n'] == 1:
            return True
        return False

    def delete_many(self, query):
        """
            Returns True if record is deleted
            Else False
        """
        if Database.CURSOR.delete_many(query).raw_result['n'] > 0:
            return True
        return False

    def count_documents(self, query={}):
        return Database.CURSOR.count_documents(query)


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
    
    # Delete All Records
    print("All records Deleted!" if db.delete_many({}) else "Couldn't Find Any Record To Delete")
    
    # Display All
    pprint.pprint(db.find() if db.find() else "Couln't find any record to Display!")