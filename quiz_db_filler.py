from json import load
from models.quiz import Quiz
content = load(open('json_quiz.json'))
for question in content:
    Quiz(question=question.get('question'), options=question.get('options'), answer=question.get('answer')).save_quiz() 
