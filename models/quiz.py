try:
    from models.database import Database
except ImportError:
    from database import Database

try:
    from models.users import User
except:
    from users import User

from bson import ObjectId

class Quiz:

    COLLECTION = "Quiz"
    DB = Database()

    def __init__(self,
                 question=None,
                 category=None,
                 options=[],
                 answer=None,
                 attempts=dict(),
                 _id=None,
                 ):

        self.question = question
        self.category = category
        self.options = options
        self.answer = answer
        self.attempts = attempts
        self._id = _id

    def to_dict(self):
        result = {
            "question": self.question,
            "category": self.category,
            "options": self.options,
            "answer": self.answer,
            "attempts": self.attempts
        }

        if self._id:
            result['_id'] = self._id

        return result

    @classmethod
    def to_class(cls, json_dict):
        if json_dict:
            return cls(**json_dict)

    def save_quiz(self):
        return Quiz.DB.insert_one(Quiz.COLLECTION, self.to_dict())

    def update_quiz_info(self):
        Quiz.DB.update_one(
            Quiz.COLLECTION,
            {"_id": self._id},
            {'$set': self.to_dict()}
        )

    @staticmethod
    def get_questions(userID, limit=10):
        pipeline = [
            {
                "$project": {
                    "questions": "$question",
                    "options": "$options",
                    "answer": "$answer",
                }
            },
            {
                "$match": {
                    "_id": {
                        "$not": {
                            "$in": "$attempts"
                        }
                    }
                }
            },
            {
                "$limit": limit
            }
        ]
        return list(Quiz.DB.CURSOR[Quiz.COLLECTION].aggregate(pipeline))

    @staticmethod
    def get_attempts(limit=10, skip=10):
        pass

    @staticmethod
    def attempt_question(userID, answer, question):
        result = question.answer == answer
        question.attempts.update({userID: {"is_correct": result}})
        question.update_quiz_info()
        return result


if __name__ == "__main__":
    q1 = Quiz(
        question="What ka matlab kya hai?",
        category="random",
        options=[
            'Kya hai?', 'Kya hai??', 'Kya hai', 'kya'
        ],
        answer='kya',
        _id=ObjectId("5e3d8709d05d92db07c4c739")
    )

    q2 = Quiz(
        question="Why dis Kolaveri Di?",
        category="random",
        options=[
            'Di', 'DiDi', 'DiDiDi', 'Di!!'
        ],
        answer='Di'
    )

    # q1.save_quiz()
    # q2.save_quiz()
    # print(User.get_all_users()[0])
    usr = User.get_user_info(_id=User.get_all_users()[0]['_id'])
    print(Quiz.attempt_question(usr._id, "kyas", q1))
    # print(usr)
