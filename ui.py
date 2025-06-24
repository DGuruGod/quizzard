from kivy.core.window import Window
from kivy.properties import StringProperty
from kivy.uix.modalview import ModalView
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.screenmanager import Screen
from kivy.uix.image import Image, AsyncImage
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.uix.spinner import Spinner
from kivymd.uix.button import MDRaisedButton
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from categories import CATEGORY_MAP



class BtnBhv(ButtonBehavior, Image):
    pass

class StartScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', padding=40, spacing=20)

        # Category spinner
        self.category_spinner = Spinner(
            text='Select Category',
            values=[f"{k}" for k, v in CATEGORY_MAP.items()],
            size_hint=(None, None), size=(300, 44),pos_hint={'center_x':0.5,'center_y':0.7}
        )

        # Difficulty spinner
        self.difficulty_spinner = Spinner(
            text='Select Difficulty',
            values=('easy', 'medium', 'hard'),
            size_hint=(None, None), size=(300, 44),pos_hint={'center_x':0.5,'center_y':0.5}
        )


        # Start button
        start_button = MDRaisedButton(
            text='Start Quiz',
            size_hint=(None, None), size=(300, 44),
            pos_hint={'center_x': 0.5},
            on_release=self.start_quiz
        )

        layout.add_widget(self.category_spinner)
        layout.add_widget(self.difficulty_spinner)
        layout.add_widget(start_button)

        self.add_widget(layout)

    def start_quiz(self, *args):
        category_label = self.category_spinner.text
        difficulty = self.difficulty_spinner.text

        # Ensure valid selections
        if category_label.startswith('Select') or difficulty.startswith('Select') :
            print("Please select all options.")
            return

        # Extract number from "General Knowledge (9)"
        category_number = category_label.split('(')[-1].strip(')')

        app = App.get_running_app()
        app.start_quiz(category_number, difficulty)


class DisplayScreen(Screen):
    display_text = StringProperty("")

    def __init__(self, quiz_brain, **kwargs):
        super().__init__(**kwargs)
        self.selected_option = None
        self.quiz = quiz_brain
        self.display_text = self.quiz.next_question()
        self.selected_image = None
        self.selected_btn = None
        self.dialog = None

    def pressed(self, btn_id):
        if self.selected_image:
            self.remove_widget(self.selected_image)

        if btn_id == 'trueBtn':
            self.selected_option = 'True'
            btn = self.ids.trueBtn
            tick_y = btn.top + 10
        elif btn_id == 'falseBtn':
            self.selected_option = 'False'
            btn = self.ids.falseBtn
            tick_y = btn.y - 40
        else:
            return

        tick = AsyncImage(
            source='assets/ticksign.png',
            size_hint=(None, None),
            size=(30, 30),
            pos=(btn.center_x - 15, tick_y)
        )
        self.add_widget(tick)
        self.selected_image = tick

    def next_pressed(self):
        if not self.selected_option:
            return

        is_correct = self.quiz.check_answer(self.selected_option)
        self.show_popup(is_correct)

        if self.selected_image:
            self.remove_widget(self.selected_image)
        self.selected_image = None
        self.selected_option = None

    def show_popup(self, correct):
        self.popup = ModalView(size_hint=(None, None), size=(500, 500), background_color=(0, 0, 0, 0), auto_dismiss=False)
        layout = FloatLayout()
        popup_img = Image(source='assets/popUpPlate.png', size_hint=(None, None), size=(500, 500), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        layout.add_widget(popup_img)

        if correct:
            text = 'Correct!'
        else:
            correct_ans = 'True' if self.selected_option == 'False' else 'False'
            text = f"You're Wrong!\n\nThe right option is {correct_ans}"

        label = Label(
            text=text, padding=5,
            font_size='30sp', font_name='Minicupcake.otf',
            bold=True, color=(0.2, 0.2, 0.2, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        layout.add_widget(label)

        self.popup.add_widget(layout)
        layout.opacity = 0
        Animation(opacity=1, duration=0.4).start(layout)
        self.popup.open()

        def continue_after_popup(*_):
            anim_out = Animation(opacity=0, duration=0.4)
            anim_out.bind(on_complete=lambda *_: self.popup.dismiss())
            anim_out.start(layout)

        def go_next(*_):
            if self.quiz.still_has_questions():
                self.display_text = self.quiz.next_question()
            else:
                result_screen = self.manager.get_screen('result')
                result_screen.set_score(self.quiz.score, len(self.quiz.question_list))
                self.manager.current = 'result'

        Clock.schedule_once(continue_after_popup, 1)
        Clock.schedule_once(go_next, 1.4)


class ResultScreen(Screen):
    final_score = StringProperty("")

    def set_score(self, score, total):
        self.final_score = f"Quiz Over\n\nYou scored {score}/{total}"

    def reset_quiz(self):
        app = App.get_running_app()
        app.screen_manager.current = 'start'

    def quit_app(self):
        Window.close()
