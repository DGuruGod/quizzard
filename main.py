
from kivy.lang import Builder
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from kivy.uix.image import Image
from kivymd.toast import toast
from question_model import Question
from quiz_brain import QuizBrain
from ui import DisplayScreen, ResultScreen, StartScreen
import requests


class BtnBhv(ButtonBehavior, Image):
    pass


class Quiz(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.theme_style = "Light"
        self.title = "Quiz App"

        Builder.load_file('quiz.kv')
        self.screen_manager = ScreenManager()
        # Add StartScreen for parameter selection
        self.start_screen = StartScreen(name="start")
        self.screen_manager.add_widget(self.start_screen)

        return self.screen_manager

    def start_quiz(self, category, difficulty):
        parameters = {
            'amount': 10,             # default number of questions
            'category': category,
            'difficulty': difficulty,
            'type': 'boolean'         # fixed to boolean
        }

        try:
            response = requests.get('https://opentdb.com/api.php', params=parameters)
            print(response)
            response.raise_for_status()
            print(response.text)
            question_data = response.json()['results']
            print(question_data)
            if not question_data:
                toast("No questions found. Try different settings.")
                self.screen_manager.current = "start"
                return

        except Exception as e:
            toast(f"Error: {e}")
            self.screen_manager.current = "start"
            return

        question_bank = []
        for question in question_data:
            q_text = question["question"]
            q_answer = question["correct_answer"]
            question_bank.append(Question(q_text, q_answer))

        self.quiz = QuizBrain(question_bank)
        for screen_name in ['mainscreen', 'result']:
            if self.screen_manager.has_screen(screen_name):
                screen = self.screen_manager.get_screen(screen_name)
                self.screen_manager.remove_widget(screen)

        display_screen = DisplayScreen(name="mainscreen", quiz_brain=self.quiz)
        result_screen = ResultScreen(name="result")

        self.screen_manager.add_widget(display_screen)
        self.screen_manager.add_widget(result_screen)

        self.screen_manager.current = "mainscreen"


if __name__ == "__main__":
    Quiz().run()
