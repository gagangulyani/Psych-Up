try:
    from models.quiz import Quiz
    from models.users import User
    from models.database import Database
except:
    from quiz import Quiz
    from users import User
    from database import Database
finally:
    from pymongo import MongoClient
    from bson import ObjectId
    
class Controller(object):
    pass