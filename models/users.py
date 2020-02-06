try:
    from models.database import Database
except ImportError:
    from database import Database

from pprint import pprint
from bson import ObjectId


class User:

    DB = Database(COLLECTION='Users')

    def __init__(
        self,
        username,
        password,
        age=0,
        name=None,
        number_of_wins=0,
        history=[],
        _id=None,
        followers=[],
        following=[],
        total_score=0
    ):
        self.name = name
        self.username = username
        self.password = password
        self.age = age
        self.number_of_wins = number_of_wins
        self.history = history
        self._id = _id
        self.followers = followers
        self.following = following
        self.total_score = total_score
        self.user_db = User.DB

    def to_dict(self):
        """
            Returns a Dictionary object consisting of Data Members of User Class

        """
        result = {
            "name": self.name,
            "username": self.username,
            "password": self.password,
            "age": self.age,
            "number_of_wins": self.number_of_wins,
            "history": self.history,
            "followers": self.followers,
            "following": self.following,
            "total_score": self.total_score
        }

        if self._id:
            result.update({'_id': self._id})

        return result

    @classmethod
    def to_class(cls, dict_obj):
        if dict_obj:
            return cls(**dict_obj)

    def display_user_info(self):
        pprint(self.to_dict())

    def save_user(self):
        _id = self.user_db.insert_one(self.to_dict())
        self._id = _id
        return _id

    def get_user(self, username=True, _id=False):
        if username:
            return User.to_class(self.user_db.find_one({'username': self.username}))
        elif _id:
            return User.to_class(self.user_db.find_one({'_id': self._id}))

    @staticmethod
    def get_user_info(username=None, _id=None):
        if username:
            return User.to_class(User.DB.find_one({'username': username}))
        elif _id:
            return User.to_class(User.DB.find_one({'_id': _id}))

    def update_user_info(self):
        self.user_db.update_one(
            {"_id": self._id},
            {'$set': self.to_dict()}
        )

    def delete_user(self):
        return self.user_db.delete_one({'_id': self._id})

    def follow_user(self, user):

        followed = False

        if self._id not in user.followers:
            user.followers.append(self._id)
            followed = True

        if user._id not in self.following:
            self.following.append(user._id)
            followed = True

        if followed:
            self.update_user_info()
            user.update_user_info()

        return followed

    def unfollow_user(self, user):
        unfollowed = False
        if self._id in user.followers:
            user.followers.remove(self._id)
            unfollowed = True

        if user._id in self.following:
            self.following.remove(user._id)
            unfollowed = True

        if unfollowed:
            self.update_user_info()
            user.update_user_info()

        return unfollowed

    def get_followers(self, limit=0):
        # finds all users user is following
        pipeline = [
            {
                "$graphLookup": {
                    "from": "Users",
                    "startWith": "$followers",
                    "connectFromField": "followers",
                    "connectToField": "_id",
                    "as": "followers"
                }
            },
            {
                "$match": {
                    "_id": self._id
                }
            },
            {
                "$project": {
                    "name": 1,
                    "followers": "$followers",
                }
            }
        ]

        if limit:
            pipeline.append({'$limit': limit})

        return list(self.user_db.CURSOR.aggregate(pipeline))

    def get_following(self, limit=0):
        # finds all users self is following
        pipeline = [
            {
                "$graphLookup": {
                    "from": "Users",
                    "startWith": "$following",
                    "connectFromField": "following",
                    "connectToField": "_id",
                    "as": "following"
                }
            },
            {
                "$match": {
                    "_id": self._id
                }
            },
            {
                "$project": {
                    "name": 1,
                    "_id": 1,
                    "following": "$following",
                }
            }
        ]

        if limit:
            pipeline.append({'$limit': limit})

        return list(self.user_db.CURSOR.aggregate(pipeline))

    def play_quiz(self):
        pass

    @staticmethod
    def get_all_users():
        return User.DB.find()

    def __repr__(self):
        return str(
            {
                "name": self.name,
                "username": self.username,
                "password": self.password,
                "age": self.age,
                "number_of_wins": self.number_of_wins,
                "history": self.history,
                "followers": self.followers,
                "following": self.following,
                "total_score": self.total_score,
                "_id": self._id
            }
        )


if __name__ == "__main__":
    usr1 = User.get_user_info(_id=User.get_all_users()[0]['_id'])
    print(usr1)
