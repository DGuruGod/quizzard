from kivy.core.window import Window
from kivy.properties import StringProperty
from kivy.uix.modalview import ModalView
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.screenmanager import Screen
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.animation import Animation
from question_model import Question
from data import question_data
from quiz_brain import QuizBrain


class BtnBhv (ButtonBehavior,Image):
    pass

class DisplayScreen(Screen):
    display_text = StringProperty("")

    def __init__(self, quiz_brain, **kwargs):
        super().__init__(**kwargs)
        self.selected_option = None
        self.quiz = quiz_brain
        self.display_text = self.quiz.next_question()
        # To hold tick reference
        self.selected_image = None
        self.selected_btn = None
        self.dialog = None

    def pressed(self, btn_id):
        # Remove old tick if it exists
        if self.selected_image:
            self.remove_widget(self.selected_image)

        # Set selection and determine tick position
        if btn_id == 'trueBtn':
            self.selected_option = 'True'
            btn = self.ids.trueBtn
            tick_y = btn.top + 10  # above
        elif btn_id == 'falseBtn':
            self.selected_option = 'False'
            btn = self.ids.falseBtn
            tick_y = btn.y - 40  # below
        else:
            return

        # Create tick image
        tick = Image(
            source='assets/ticksign.png',
            size_hint=(None, None),
            size=(30, 30),
            pos=(btn.center_x - 15, tick_y)
        )

        self.add_widget(tick)
        self.selected_image = tick


    def next_pressed(self):
        if not self.selected_option:
            return  # No selection made

        is_correct = self.quiz.check_answer(self.selected_option)
        self.show_popup(is_correct)

        # Clear tick and selection
        if self.selected_image:
            self.remove_widget(self.selected_image)
        self.selected_image = None
        self.selected_option = None

    def show_popup(self,correct):
        # Create the popup
        self.popup = ModalView(size_hint=(None, None), size=(250, 250),  background_color=(0, 0, 0, 0),
                               auto_dismiss=False)

        layout = FloatLayout()

        # pop up display
        img_source = 'assets/popUpPlate.png'
        popup_img = Image(source=img_source, size_hint=(1, 1),pos_hint={'center_x':0.5,'center_y':0.5})
        layout.add_widget(popup_img)

        #  label display if answer is correct or not
        if correct :
            label = Label(
                text='Correct!', padding = 5,
                font_size='20sp',font_name='Minicupcake.otf',
                bold=True,
                color=(0.2, 0.2, 0.2, 1),  # White text
                pos_hint={'center_x': 0.5, 'center_y': 0.5}
            )
            layout.add_widget(label)

        elif self.selected_option =='False':
            label = Label(
                text="You're Wrong! \n \n The right option is True",
                font_size='18sp',font_name='Minicupcake.otf',
                bold=True, padding = 5,
                color=(0.2, 0.2, 0.2, 1),  # White text
                pos_hint={'center_x': 0.5, 'center_y': 0.5}
            )
            layout.add_widget(label)
        elif self.selected_option =='True':
            label = Label(
                text="You're Wrong! \n \n The right option is False",
                font_size='18sp',font_name='Minicupcake.otf',
                bold=True, padding = 5,
                color=(0.2, 0.2, 0.2, 1),  # White text
                pos_hint={'center_x': 0.5, 'center_y': 0.5}
            )
            layout.add_widget(label)

        self.popup.add_widget(layout)

        # Fade in animation
        layout.opacity = 0
        anim_in = Animation(opacity=1, duration=0.4)
        anim_in.start(layout)

        self.popup.open()

        # Fade out and dismiss after 3 seconds
        def continue_after_popup(*_):
            anim_out = Animation(opacity=0, duration=0.4)
            anim_out.bind(on_complete=lambda *_: self.popup.dismiss())
            anim_out.start(layout)

        #display next question/result page after pop up
        def go_next(*_):
            if self.quiz.still_has_questions():
                self.display_text=self.quiz.next_question()
            else:
                result_screen = self.manager.get_screen('result')
                result_screen.set_score(self.quiz.score, len(self.quiz.question_list))
                self.manager.current = 'result'
                #Reset tick and selection
            if self.selected_image:
                self.remove_widget(self.selected_image)
                self.selected_image = None
                self.selected_option = None

        Clock.schedule_once(continue_after_popup, 1)
        Clock.schedule_once(go_next, 1)  # Wait until after popup is dismissed


class ResultScreen(Screen):
    final_score = StringProperty("")

    #final score display
    def set_score(self,score,total):
        self.final_score = f"Quiz Over\n\nYou scored {score}/{total}"

    def reset_quiz(self):
        question_bank = []
        for question in question_data:
            question_text = question["question"]
            question_answer = question["correct_answer"]
            new_question = Question(question_text, question_answer)
            question_bank.append(new_question)

        self.quiz = QuizBrain(question_bank)

        # Reset display screen UI
        from kivy.app import App

        display_screen = App.get_running_app().root.get_screen("mainscreen")
        display_screen.quiz = self.quiz
        display_screen.display_text = self.quiz.next_question()

    def quit_app(self):
        Window.close()  #  exits the Kivy window (cross-platform)

