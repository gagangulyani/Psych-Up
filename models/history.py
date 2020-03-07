from models.database import Database
from models.users import User
from pymongo import DESCENDING


class History(object):
    """
        for LeaderBoard
    """
    COLLECTION = "User_History"

    def __init__(self,
                 name,
                 userID,
                 score,
                 num_of_question=0,
                 _id=None
                 ):
        self.userID = userID
        self.name = name
        self.score = score
        self.num_of_question = score // 10
        self._id = _id

    def to_dict(self):
        temp = {
            'name': self.name,
            "userID": self.userID,
            "score": self.score,
            "num_of_question": self.num_of_question
        }
        if self._id:
            temp.update({'_id': self._id})
        return temp

    @classmethod
    def to_class(cls, dict_obj):
        if dict_obj:
            # print(dict_obj)
            return cls(**dict_obj)

    @staticmethod
    def show_history(userID=None):
        query = {}
        if userID:
            query = {
                'userID': userID
            }
        return [
            History.to_class(i) for i in Database.find(
                COLLECTION=History.COLLECTION,
                query=query,
                sort=[('score', DESCENDING)],
                limit=10
            )
        ]

    def save_history(self):
        return Database.insert_one(
            COLLECTION=History.COLLECTION, dict_=self.to_dict()
        )

    @staticmethod
    def find_and_update(userID, score):
        # for storing highscore of users in history

        user = History.to_class(Database.find_one(
            History.COLLECTION, {'userID': userID}))

        if user:
            print('user score: {}\nscore by routes: {}'.format(user.score, score))
            if user.score < score:
                user.score = score
                user.num_of_question = score // 10
                user._id = None

                return Database.update_one(
                    COLLECTION=History.COLLECTION,
                    query={'userID': userID},
                    update_query={'$set': user.to_dict()}
                )
        else:
            user = User.get_user_info(_id=userID)
            History(name=user.name, userID=userID, score=score).save_history()

    @staticmethod
    def delete_history(history_id=None, userID=None):
        if userID:
            return Database.delete_one(COLLECTION=History.COLLECTION,
                                       query={'userID': userID})
        return Database.delete_one(COLLECTION=History.COLLECTION,
                                   query={'_id': history_id})
