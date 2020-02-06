from models.database import Database


class Quiz:

    def __init__(self,
                 question=None,
                 category=None,
                 options=[],
                 answer=None,
                 scoreboard=[],
                 _id=None,
                 ):

        self.question = question
        self.category = category
        self.options = options
        self.answer = answer
        self.scoreboard = scoreboard
        self._id = _id

    def to_json(self):
        result = {
            "question": self.question,
            "category": self.category,
            "options": self.options,
            "answer": self.answer,
            "scoreboard": self.scoreboard
        }

        if self._id:
            result['_id'] = self._id

        return result

    @classmethod
    def to_class(cls, json_dict):
        if json_dict:
            return cls(**json_dict)
