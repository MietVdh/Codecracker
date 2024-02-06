from kivy.config import Config

Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'height', '700')
Config.set('graphics', 'width', '850')

import random
from kivy.app import App

from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.stacklayout import StackLayout

BLACK = ("BLACK", (0, 0, 0))
WHITE = ("WHITE", (1, 1, 1))
RED = ("RED", (1, 0, 0))
YELLOW = ("YELLOW", (1, 1, 0))
BLUE = ("BLUE", (0, 0, 1))
GREEN = ("GREEN", (0, 1, 0))
PURPLE = ("PURPLE", (0.5, 0, 0.5))
ORANGE = ("ORANGE", (1, 0.6, 0))
BROWN = ("BROWN", (0.65, 0.2, 0.65))
GREY = ("GREY", (0.5, 0.5, 0.5))
LIGHT_GREY = ("LIGHT_GREY", (0.75, 0.75, 0.75))
MAGENTA = ("MAGENTA", (1, 0, 1))
CYAN = ("CYAN", (0, 0.95, 1))
FOREST_GREEN = ("FOREST_GREEN", (0.15, 0.5, 0.15))
MAUVE = ("MAUVE", (0.9, 0.7, 1))
LIGHT_YELLOW = ("LIGHT_YELLOW", (1, 1, 0.85))
LIGHT_ORANGE = ("LIGHT_ORANGE", (1, 0.95, 0.85))
LIGHT_BLUE = ("LIGHT_BLUE", (0.8, 0.9, 1))
DARKER_BLUE = ("DARKER_BLUE", (0.25, 0.45, 0.75))



BACKGROUND_COLOUR = LIGHT_BLUE
SECOND_COLOUR = DARKER_BLUE
PEG_BACKGROUND_COLOUR = LIGHT_GREY

NUMBER_OF_GUESSES = 12
DEFAULT_CODE_LENGTH = 5
DEFAULT_NUM_OF_COLOURS = 8
DEFAULT_UNIQUE = True

number_of_colours = DEFAULT_NUM_OF_COLOURS
unique = DEFAULT_UNIQUE
code_length = DEFAULT_CODE_LENGTH

new_num_of_colours = number_of_colours
new_unique = unique
new_code_length = code_length

Window.clearcolor = LIGHT_BLUE[1]

COLOURS = [BLACK, WHITE, RED, YELLOW, BLUE, GREEN, PURPLE, ORANGE, MAGENTA, FOREST_GREEN, MAUVE]

instructions_text = '''
The goal of the game is to guess the secret code that was generated by the computer.
To do this, you will input guesses, and receive feedback on each guess.
A black peg means you correctly guessed a colour AND position. A white peg means you correctly guessed a colour, but you got the position wrong.
Feedback pegs are ordered by colour - their position is not meaningful.\n
To play to game, click on the buttons at the bottom of your screen.
A colour menu will pop up.
Choose a colour from the menu. Repeat for the remaining input spots.
When you have chosen a colour for each position, click the submit button. To clear your current guess, click the X.\n
Keep guessing, using the feedback provided, until you crack the code.
Good luck!

'''


secret_code = [None] * code_length

def generate_code(code_length, unique, number_of_colours):
    # Get a code generated automatically, using settings set by user (or defaults)
        code = []
        available_colours = COLOURS[:number_of_colours]
        if not unique:
            available_colours += available_colours
        for i in range(code_length):
            idx = random.randint(0, len(available_colours)-1)
            code.append(available_colours.pop(idx))
        return code



def get_feedback(secret_code, guess, unique=True):
        feedback = []
        if unique:
            for i in range(len(guess)):
                if secret_code[i] == guess[i]:
                    feedback.append(BLACK)
                elif guess[i] in secret_code:
                    feedback.append(WHITE)
        else:
            secret_code_clone = secret_code[:]
            guess_clone = guess[:]
            for i in range(len(guess_clone)):
                if secret_code_clone[i] == guess_clone[i]:
                    feedback.append(BLACK)
                    secret_code_clone[i] = None
                    guess_clone[i] = None
            for i in range(len(guess)):
                if guess_clone[i] is None:
                    continue
                elif guess_clone[i] in secret_code_clone:
                    feedback.append(WHITE)
                    idx = secret_code_clone.index(guess_clone[i])
                    secret_code_clone[idx] = None

        feedback.sort()
        return feedback



class RootLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.code_length = DEFAULT_CODE_LENGTH
        self.unique = DEFAULT_UNIQUE
        self.number_of_colours = DEFAULT_NUM_OF_COLOURS
        self.secret_code = generate_code(self.code_length, self.unique, self.number_of_colours)

        global secret_code
        secret_code = self.secret_code

        self.left_pane = LeftPane(self)
        self.right_pane = RightPane(self)
        self.add_widget(self.left_pane)
        self.add_widget(self.right_pane)


    def reveal_code(self):
        code = self.left_pane.top_frame.the_secret_code
        code.reveal_secret_code()
        self.left_pane.input_frame.disable_btns()

    def on_submit(self):
        inputframe = self.left_pane.input_frame
        guesses_frame = self.left_pane.guesses_frame
        current_guess = inputframe.guess

        # Empty guess does not get submitted
        if current_guess.guess == [None] * code_length:
            return

        next_guess = guesses_frame.children[self.num_of_guesses]
        next_guess.set_code(current_guess.guess)
        next_guess.add_feedback(self.secret_code)
        self.num_of_guesses += 1
        if self.num_of_guesses == 12:
            self.reveal_code()
        current_guess.clear()

    def restart(self):
        global number_of_colours, code_length, unique, secret_code

        number_of_colours = new_num_of_colours
        code_length = new_code_length
        unique = new_unique if code_length <= number_of_colours else False

        self.secret_code = generate_code(code_length, unique, number_of_colours)
        secret_code = self.secret_code
        self.remove_widget(self.left_pane)
        self.remove_widget(self.right_pane)
        self.left_pane = LeftPane(self)
        self.add_widget(self.left_pane)
        self.add_widget(self.right_pane)
        self.num_of_guesses = 0
        self.left_pane.input_frame.enable_btns()

    def display_instructions(self):
        popup = Popup(title="How to play")
        popup.size_hint = (None, None)
        popup.size = (600, 400)
        content = BoxLayout()
        content.orientation = 'vertical'
        content.padding = [0, 0, 0, 20]
        label = Label()
        btn = Button()
        btn.text = "OK"
        btn.bind(on_press = popup.dismiss)
        btn.background_color = SECOND_COLOUR[1]
        btn.background_normal = ""
        btn.size_hint = 0.2, 0.2
        btn.pos_hint = {'x': 0.4}
        label.text = instructions_text
        content.add_widget(label)
        content.add_widget(btn)
        popup.content = content

        popup.open()

    num_of_guesses = 0


class LeftPane(BoxLayout):
    def __init__(self, root_layout, **kwargs):
        super().__init__(**kwargs)

        self.root_layout = root_layout
        self.top_frame = TopFrame(self.root_layout)
        self.guesses_frame = GuessesFrame(self)
        self.input_frame = InputFrame(self.root_layout)

        self.add_widget(self.top_frame)
        self.add_widget(self.guesses_frame)
        self.add_widget(self.input_frame)

class RightPane(BoxLayout):
    def __init__(self, root_layout, **kwargs):
        super().__init__(**kwargs)

        self.root_layout = root_layout


class TopFrame(BoxLayout):
    def __init__(self, root_layout, **kwargs):
        super().__init__(**kwargs)

        self.root_layout = root_layout
        self.the_secret_code = SecretCode()
        self.the_secret_code.code = secret_code
        self.add_widget(self.the_secret_code)

        self.reveal_button = Button()
        self.reveal_button.size_hint = (None, None)
        self.reveal_button.size = (code_length * 25, 36)
        self.reveal_button.text = "Reveal"
        self.reveal_button.on_press = self.root_layout.reveal_code
        self.reveal_button.background_color = SECOND_COLOUR[1]
        self.reveal_button.background_normal = ''

        self.add_widget(self.reveal_button)



class GuessesFrame(BoxLayout):
    def __init__(self, left_pane, **kwargs):
        super().__init__(**kwargs)
        self.guesses = []

        self.left_pane = left_pane
        for i in range(NUMBER_OF_GUESSES):
            gl = GuessLine(self, i)
            self.guesses.append(gl)
            self.add_widget(gl)


class InputFrame(BoxLayout):

    def __init__(self, root_layout, **kwargs):
        super().__init__(**kwargs)
        self.root_layout = root_layout

        self.guess = Guess()

        self.clear_btn = Button()
        self.clear_btn.text = "X"
        self.clear_btn.size_hint = (None, None)
        self.clear_btn.size = (36, 36)
        self.clear_btn.background_color = SECOND_COLOUR[1]
        self.clear_btn.background_normal = ''
        self.clear_btn.on_press = self.clear_guess

        self.submit_btn = Button()
        self.submit_btn.text = "Submit"
        self.submit_btn.size_hint = (None, None)
        btn_length = code_length * 25 - 40
        if btn_length < 50:
            btn_length = 50
        self.submit_btn.size = (btn_length, 36)
        self.submit_btn.on_press = self.root_layout.on_submit
        self.submit_btn.background_color = SECOND_COLOUR[1]
        self.submit_btn.background_normal = ''

        self.add_widget(self.guess)
        self.add_widget(self.clear_btn)
        self.add_widget(self.submit_btn)

    def clear_guess(self):
        self.guess.clear()

    def disable_btns(self):
        for child in self.guess.children:
            child.disabled = True
        self.submit_btn.disabled = True
        self.clear_btn.disabled = True

    def enable_btns(self):
        for child in self.guess.children:
            child.disabled = False
        self.submit_btn.disabled = False
        self.clear_btn.disabled = False


class SettingsPane(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_code_length_slider_change(self, slider):
        global new_code_length
        new_code_length = int(slider.value)

    def on_switch_active(self, switch):
        global new_unique
        new_unique = bool(switch.active)


    def on_num_of_colours_slider_change(self, slider):
        global new_num_of_colours
        new_num_of_colours = int(slider.value)


class GuessLine(BoxLayout):
    def __init__(self, frame, number, **kwargs):
        super().__init__(**kwargs)

        self.guesses_frame = frame
        self.code = Code()
        self.feedback = Feedback()
        self.add_widget(self.code)
        self.add_widget(self.feedback)
        self.number = number

    def add_feedback(self, secret_code):
        code = self.code.code
        result = get_feedback(secret_code, code)

        if result == [BLACK] * code_length:
            self.guesses_frame.left_pane.root_layout.reveal_code()

        self.feedback.set_feedback(result)

    def set_code(self, code):
        self.code.set_code(code)


class Code(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.code = []
        self.buttons = []
        self.size = (code_length * 45, 0)

        for i in range(code_length):
            c = CodeButton(self, i)
            self.buttons.append(c)
            self.code.append(None)
            self.add_widget(c)

    def update_display(self):
        for i in range(code_length):
            new_colour = self.code[i]
            if (new_colour):
                for child in self.children:
                    if i == child.spot:
                        child.update_colour(new_colour)

    def set_code(self, new_code):
        self.code = new_code
        self.update_display()


class CodeButton(Button):
    def __init__(self, code_line, spot, **kwargs):
        super().__init__(**kwargs)
        self.background_color = LIGHT_GREY[1]
        self.code_line = code_line
        self.colour = LIGHT_GREY
        self.spot = spot

    def update_colour(self, colour):
        self.disabled_color = colour[1]
        self.background_color = colour[1]
        self.colour = colour
        # self.text = colour[0]
        self.disabled = False


class Feedback(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.feedback = []
        for i in range(code_length):
            c = FeedbackButton()
            self.feedback.append(None)
            c.background_color = LIGHT_GREY[1]
            self.add_widget(c)

    def set_feedback(self, feedback):
        self.feedback = feedback
        while len(self.feedback) < code_length:
            self.feedback.append(None)
        for i, feedback_btn in enumerate(self.children):
            if feedback[i]:
                feedback_btn.set_colour(feedback[i])


class CodeGuessButton(Button):
    def __init__(self, guess, i, **kwargs):
        super().__init__(**kwargs)
        self.i = i
        self.background_normal = ''
        self.guess = guess
        self.colour = GREY

        self.colour_picker = ColourPicker(self, number_of_colours)

    def select_colour(self):
        self.colour_picker.open()


class Guess(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.size = (code_length * 45, 0)
        self.guess = []
        for j in range(code_length):
            c = CodeGuessButton(self, j)
            c.background_color = LIGHT_GREY[1]
            self.guess.append(None)
            self.add_widget(c)

    def clear(self):
        for btn in self.children:
            self.guess = [None] * code_length
            btn.background_color = LIGHT_GREY[1]
            btn.text = ""

    def update_pos(self, i, colour):
        self.guess[i] = colour


class FeedbackButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.colour = LIGHT_GREY

    def set_colour(self, colour):
        self.colour = colour
        self.background_color = colour[1]


class ColourPicker(Popup):
    def __init__(self, parent, num_of_colours):
        super().__init__()

        self.btn = parent
        self.title = "Choose a colour"
        self.background_color = WHITE[1]
        self.size_hint = (None, None)
        self.size = (200, 250)
        self.selected_colour = GREY

        self.content = StackLayout()

        colours = COLOURS[:num_of_colours]

        for colour in colours:
            colour_button = SelectColourButton(self)
            colour_button.size_hint = (.25, .25)
            colour_button.background_color = colour[1]
            colour_button.colour = colour
            self.content.add_widget(colour_button)

        self.reset_btn = SelectColourButton(self)
        self.reset_btn.size_hint = (.25, .25)
        self.reset_btn.background_color = LIGHT_GREY[1]
        self.reset_btn.text = 'X'
        self.content.add_widget(self.reset_btn)


class SelectColourButton(Button):
    def __init__(self, parent, **kwargs):
        super().__init__(**kwargs)
        self.picker = parent
        self.background_normal = ''
        self.colour = LIGHT_GREY

        self.on_press = self.display_colour_selected

    def display_colour_selected(self):
        guess_btn = self.picker.btn

        if self == self.picker.reset_btn:
            guess_btn.guess.update_pos(guess_btn.i, None)
            guess_btn.colour = None
            guess_btn.background_color = self.background_color
            self.picker.dismiss()
            return

        self.picker.selected_colour = self.background_color
        guess_btn.background_color = self.background_color
        guess_btn.colour = self.colour
        guess_btn.guess.update_pos(guess_btn.i, self.colour)
        text_color = WHITE[1]
        if self.colour[0] in ("WHITE", "YELLOW"):
            text_color = BLACK[1]
        guess_btn.color = text_color
        # guess_btn.text = self.colour[0]
        self.picker.dismiss()

class SecretCode(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.size_hint = (None, 1)
        self.size = (code_length * 45, 0)
        self.secret_code = secret_code
        for j, spot in enumerate(secret_code):
            code_btn = CodeButton(self, j)
            code_btn.background_normal = ''
            code_btn.background_color = SECOND_COLOUR[1]
            code_btn.colour = spot
            self.add_widget(code_btn)

    def reveal_secret_code(self):
        for child in self.children:
            child.background_color = child.colour[1]


    def reset(self):
        self.secret_code = secret_code
        for btn in self.walk():
            btn.background_color = GREY[1]


class CodeCrackerApp(App):
    pass


CodeCrackerApp().run()
