from models.database import Database
from bson import ObjectId


class Contact(object):
    COLLECTION = "Messages"

    def __init__(self,
                 email,
                 title,
                 name,
                 message="",
                 _id=None):

        self.message = message
        self.email = email
        self.title = title
        self.name = name
        self._id = _id

    def to_dict(self):
        result = {
            'message': self.message,
            'email': self.email,
            'title': self.title,
            'name': self.name,
        }
        if self._id:
            result.update({'_id': self._id})
        return result

    @classmethod
    def to_class(cls, dict_obj):
        if dict_obj:
            return cls(**dict_obj)

    def save_message(self):
        return Database.insert_one(
            COLLECTION=Contact.COLLECTION,
            dict_=self.to_dict()
        )

    @staticmethod
    def get_messages():
        return [
            Contact.to_class(i) for i in Database.find(
                COLLECTION=Contact.COLLECTION,
                query={},
                sort=[('_id', -1)]
            )
        ]

    @staticmethod
    def get_message(_id):
        return Database.find_one(
            COLLECTION=Contact.COLLECTION,
            query={
                '_id': ObjectId(_id)
            }
        )

    @staticmethod
    def delete_message(_id):
        return Database.delete_one(
            COLLECTION=Contact.COLLECTION,
            query={'_id': ObjectId(_id)}
        )
