from models.database import Database
from pprint import pprint
from bson import ObjectId
from werkzeug.security import (generate_password_hash,
                               check_password_hash)


class User:

    COLLECTION = 'Users'
    DB = Database()

    def __init__(
        self,
        username=None,
        password=None,
        email=None,
        age=0,
        name=None,
        number_of_wins=0,
        history=[],
        _id=None,
        followers=[],
        following=[],
        total_score=0,
        is_admin=False,
        active=True
    ):
        self.name = name
        self.username = username
        self.password = password
        self.email = email
        self.age = age
        self.number_of_wins = number_of_wins
        self.history = history
        self._id = _id
        self.is_admin = is_admin
        self.followers = followers
        self.following = following
        self.total_score = total_score
        self.active = active

    def to_dict(self, signup=False):
        """
            Returns a Dictionary object consisting of Data Members of User Class

        """

        if signup:
            self.password = generate_password_hash(password=self.password,
                                                   method="pbkdf2:sha512")
        result = {
            "name": self.name,
            "username": self.username,
            "password": self.password,
            "email": self.email,
            "age": self.age,
            "number_of_wins": self.number_of_wins,
            "history": self.history,
            "followers": self.followers,
            "following": self.following,
            "is_admin": self.is_admin,
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

    def save_user(self, signup=False):
        _id = User.DB.insert_one(User.COLLECTION, self.to_dict(signup=signup))
        self._id = _id
        print(self._id)
        return _id

    @staticmethod
    def login(username, password):
        if usr := User.DB.find_one(
            COLLECTION=User.COLLECTION,
            query={"$or": [{"username": username},
                           {"email": username}]}
        ):
            if check_password_hash(usr.get('password'), password):
                return usr
            return False

    def get_user(self, username=True, _id=False):
        if username:
            return User.to_class(User.DB.find_one(User.COLLECTION, {'username': self.username}))
        elif _id:
            return User.to_class(User.DB.find_one(User.COLLECTION, {'_id': self._id}))

    @staticmethod
    def get_user_info(username=None, _id=None, email=None):
        if username:
            return User.to_class(User.DB.find_one(User.COLLECTION, {'username': username}))
        elif _id:
            return User.to_class(User.DB.find_one(User.COLLECTION, {'_id': _id}))
        return User.to_class(User.DB.find_one(User.COLLECTION, {'email': email}))

    def update_user_info(self):
        User.DB.update_one(User.COLLECTION,
                           {"_id": self._id},
                           {'$set': self.to_dict()}
                           )

    def delete_user(self):
        return User.DB.delete_one(User.COLLECTION, {'_id': self._id})

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

        return list(User.DB.CURSOR[User.COLLECTION].aggregate(pipeline))

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

        return list(User.DB.CURSOR[User.COLLECTION].aggregate(pipeline))

    def play_quiz(self):
        pass

    @staticmethod
    def get_all_users():
        return User.DB.find(User.COLLECTION)

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

    def is_active(self):
        # Required by Flask Login
        return self.active

    @staticmethod
    def is_authenticated():
        # Required by Flask Login
        return True

    @staticmethod
    def is_anonymous():
        # Required by Flask Login
        return False

    def get_id(self):
        # Required by Flask Login
        return self._id


if __name__ == "__main__":
    usr1 = User.get_user_info(_id=User.get_all_users()[0]['_id'])
    usr1.name = "Gagan Gulyani"
    usr1.update_user_info()
    usr2 = User.get_user_info(_id=User.get_all_users()[1]['_id'])
    usr2.follow_user(usr1)

    print(usr1.get_followers())
    # print(usr1.get_user(username=usr1.username))
