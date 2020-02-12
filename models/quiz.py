from models.database import Database
from models.users import User
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
                 userID=None
                 ):

        self.question = question
        self.category = category
        self.options = options
        self.answer = answer
        self.attempts = attempts
        self.userID = userID
        self._id = _id

    def to_dict(self):
        result = {
            "question": self.question,
            "category": self.category,
            "options": self.options,
            "answer": self.answer,
            "attempts": self.attempts,
            "userID": self.userID
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
    def get_questions(userID, limit=10, show_history=False, is_admin=False):

        display_new_questions = show_history

        pipeline = [
            {
                '$project': {
                    'question': '$question',
                    'options': '$options',
                    'answer': '$answer',
                    'attempts': '$attempts'
                }
            },
            {
                '$match': {
                    '$or': [
                        {
                            f'attempts.{str(userID)}.is_correct': False
                        },
                        {
                            f'attempts.{str(userID)}': {
                                '$exists': display_new_questions
                            }
                        }
                    ],
                }
            },
            {
                "$limit": limit
            }
        ]
        if show_history:
            # deleting query
            # which created a filter to display quesions which user attempted
            del pipeline[1]['$match']['$or'][0]
            # print(pipeline)

        if is_admin:
            # if is_admin, questions posted
            # by admin won't be displayed!
            pipeline[1]['$match'].update({
                "posted_by": {"$ne": userID}
            })

        return [
            Quiz.to_class(i) for i in list(
                Quiz.DB.CURSOR[Quiz.COLLECTION].aggregate(pipeline)
            )
        ]

    @staticmethod
    def get_attempts(usr):
        return Quiz.get_questions(userID=usr._id, limit=100, show_history=True)

    @staticmethod
    def attempt_question(usr, answer, question):
        # IMPORTANT: User's ObjectId is converted into string
        #            for storing it as a key in attempts Dictionary
        result = question.answer == answer
        question.attempts.update({str(usr._id): {"is_correct": result}})
        if result:
            usr.total_score += 10
            usr.update_user_info()
        question.update_quiz_info()
        return result


if __name__ == "__main__":
    # q1.save_quiz()
    # q2.save_quiz()
    # print(User.get_all_users()[0])
    users = [
        User.get_user_info(
            _id=User.get_all_users()[i]['_id']
        ) for i in range(3)
    ]

    questions = [
        Quiz.get_questions(
            userID=users[i]._id
        ) for i in range(3)
    ]

    # print(questions[0][0])

    print(Quiz.attempt_question(users[0], "kya", questions[0][0]))
    print(Quiz.attempt_question(users[1], "kyas", questions[0][0]))
    print(Quiz.attempt_question(users[2], "kyas", questions[0][0]))
    # # print(usr)

    # print("Attempts: ")
    print(Quiz.get_attempts(users[0]))
