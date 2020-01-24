from database import Database
from quiz import Quiz
from pprint import pprint


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

    @staticmethod
    def to_class(dict_obj):
        if dict_obj:
            return User(**dict_obj)

    def display_user_info(self):
        pprint(self.to_dict())

    def save_user(self):
        _id = self.user_db.insert_one(self.to_dict())
        self._id = _id

    def get_user(self, username=True, _id=False):
        if username:
            return User.to_class(self.user_db.find_one({'username': self.username}))
        elif _id:
            return User.to_class(self.user_db.find_one({'_id': self._id}))

    @staticmethod
    def get_user_info(username=None, _id=None):
        if username:
            return User.DB.find_one({'username': username})
        elif _id:
            return User.DB.find_one({'_id': _id})

    def update_user_info(self):
        self.user_db.update_one(
            {"_id": self._id},
            {'$set': self.to_dict()}
        )

    def delete_user(self):
        return self.user_db.delete_one({'_id': self._id})

    def follow_user(self, user):
        pass

    def unfollow_user(self):
        pass

    def get_followers(self):
        pass

    def get_followings(self):
        pass

    def play_quiz(self):
        pass


if __name__ == "__main__":
    usr1 = User(
        name="Gagan Deep Singh",
        username="gagangulyani",
        password='Test@Test123',
        age=21
    )

    usr1.save_user()

    # Displaying Record
    pprint(usr1.get_user().to_dict())

    # Changing Name of the user
    usr1.name = "Gagan Gulyani"

    # Updating record in User DB
    usr1.update_user_info()

    # Displaying updated Record
    pprint(usr1.get_user().to_dict())

    print("User Deleted Successfully!" if usr1.delete_user()
          else "Something Went Wrong while finding user")
