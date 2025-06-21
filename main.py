from kivy.lang import Builder
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from kivy.uix.image import Image

from question_model import Question
from data import question_data
from quiz_brain import QuizBrain
from ui import DisplayScreen, ResultScreen

question_bank = []
for question in question_data:
    question_text = question["question"]
    question_answer = question["correct_answer"]
    new_question = Question(question_text, question_answer)
    question_bank.append(new_question)

quiz = QuizBrain(question_bank)

class BtnBhv (ButtonBehavior,Image):
    pass
class Quiz(MDApp):

    def build(self):
        Builder.load_file('quiz.kv')
        self.quiz = self.create_quiz()
        sm = ScreenManager()
        sm.add_widget(DisplayScreen(name="mainscreen",quiz_brain=quiz))
        sm.add_widget(ResultScreen(name="result"))
        return sm


    def create_quiz(self):
        return QuizBrain(question_data)


if __name__ == "__main__":
    Quiz().run()
