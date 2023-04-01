import pygame
from pygame import mixer
from abc import ABC, abstractmethod
from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import Button
import random
from datetime import datetime
import os

# ----------------------------------------------------------------------------------------------  Import custom modules:
from Database import user_database


# ------------------------------------------------------------------------------------------------------------  Classes:
# Abstract class defining test environments
class TestEnvironment(ABC):
    def __init__(self, device=None, current_user=None):
        # Current user
        self.current_user = current_user
        self.device = device

        # Test parameters
        self.test_duration = 240000 / 20  # Test duration in ms (4 min by default)
        self.volume = 0.2  # Volume of the sound stimulus - Values from 0 to 1 (1 = Max volume) [%]

        # Display parameters
        self.FPS = 2000  # Frame rate celling

        # Visual stimulus parameters
        self.circle_size = 100  # Radius of the color circle stimulus [pixel]
        self.pedal_width = 150  # Width of the pedal symbol [pixel]
        self.pedal_height = 250  # Height of the pedal symbol [pixel]

        # Switch debounce time [s] - empirically measured time (countermeasure to left pedal "Switch Bounce")
        self.debounce_time = 0.2  # Could be around 190 ms

        # Style color palette
        self.GRAY = (41, 43, 45)
        self.LIGHT_GRAY = (self.GRAY[0] + 120, self.GRAY[0] + 120, self.GRAY[0] + 120)
        self.BLACK = (0, 0, 0)
        self.GREEN = (7, 169, 48)
        self.WHITE = (253, 253, 253)
        self.BLUE = (0, 0, 179)
        self.RED = (159, 0, 27)
        self.YELLOW = (255, 204, 0)
        self.color_types = [self.GREEN, self.BLUE, self.RED, self.YELLOW, self.WHITE]

        # Directory to search for dependencies
        self.project_dir = os.path.join(os.getcwd(), os.pardir)
        self.tests_style_dir = f'{self.project_dir}/Tests/Style'

        # Initialize Pygame
        pygame.init()

        # Define clock
        self.clock = pygame.time.Clock()

        # Get Monitor Info
        self.monitor_size = [pygame.display.Info().current_w, pygame.display.Info().current_h]
        self.window_width = self.monitor_size[0]
        self.window_height = self.monitor_size[1]

        # Set up the window
        self.main_window = pygame.display.set_mode((self.window_width, self.window_height), pygame.FULLSCREEN)

        # Set up sound bank
        self.high_tone = mixer.Sound(f'{self.tests_style_dir}/Sounds/High.wav')
        self.high_tone.set_volume(self.volume)
        self.low_tone = mixer.Sound(f'{self.tests_style_dir}/Sounds/Low.wav')
        self.low_tone.set_volume(self.volume)

        # Text properties [font, font size]
        title = [f'{self.tests_style_dir}/Fonts/Handgotn.ttf', 70]
        text = [f'{self.tests_style_dir}/Fonts/BebasNeue Book.ttf', 55]
        instr = [f'{self.tests_style_dir}/Fonts/BebasNeue Regular.ttf', 60]

        # Define text style
        self.title = pygame.freetype.Font(title[0], title[1])
        self.title_pos = (100, self.window_height / 6 - title[1] * 1.5)
        self.text = pygame.freetype.Font(text[0], text[1])
        self.text_pos = (150, self.window_height / 3 - text[1] * 1.5)
        self.instr = pygame.freetype.Font(instr[0], instr[1])
        self.instr_pos = (150, self.window_height / 1.05 - instr[1] * 1.5)

    # Function that remaps input from hardware buttons and presents them as a keyboard input
    @staticmethod
    def pressing_button(unicode, represented_key):
        button_event = pygame.event.Event(
            pygame.KEYDOWN,
            unicode=unicode,
            key=represented_key,
            mod=pygame.KMOD_NONE
        )
        pygame.event.post(button_event)

    def search_for_input_device(self):
        # Buttons have no hardware representation
        white_button = None
        yellow_button = None
        green_button = None
        blue_button = None
        red_button = None
        up_button = None
        down_button = None
        left_pedal = None
        right_pedal = None
        buttons = [white_button, yellow_button, green_button, blue_button,
                   red_button, up_button, down_button, left_pedal, right_pedal]

        # User chose to use control pane to control the test
        if self.device is not None and self.device.input_device == "CONTROL PANEL":
            # Protect if panel IP address is not found
            try:
                # Create a connection to the Raspberry Pi remote GPIO
                factory = PiGPIOFactory(host=self.device.device_ip)

                # Confirm connection with the panel
                panel_detected = True

                # Declare buttons and pedals based on their hardware representation
                white_button = Button(18, pin_factory=factory, pull_up=False)
                yellow_button = Button(14, pin_factory=factory, pull_up=False)
                green_button = Button(15, pin_factory=factory, pull_up=False)
                blue_button = Button(22, pin_factory=factory, pull_up=False)
                red_button = Button(27, pin_factory=factory, pull_up=False)
                up_button = Button(23, pin_factory=factory, pull_up=False)
                down_button = Button(17, pin_factory=factory, pull_up=False)
                left_pedal = Button(24, pin_factory=factory, pull_up=False)
                right_pedal = Button(25, pin_factory=factory, pull_up=False)

                buttons = [white_button, yellow_button, green_button, blue_button,
                           red_button, up_button, down_button, left_pedal, right_pedal]

                print("Panel was successfully detected")

                return panel_detected, buttons

            # Return to menu if panel is not found
            except OSError:

                panel_detected = False
                print("Panel not detected")
                return panel_detected, buttons

        # User chose keyboard to control the test
        else:
            panel_detected = False

        return panel_detected, buttons

    # Define stimulus which is being presented during the test
    def stimulus(self, question_set_index, circle_position, sound_duration):

        # Color Circles
        if question_set_index == "red":
            pygame.draw.circle(self.main_window, self.RED, circle_position, self.circle_size)

        elif question_set_index == "blue":
            pygame.draw.circle(self.main_window, self.BLUE, circle_position, self.circle_size)

        elif question_set_index == "green":
            pygame.draw.circle(self.main_window, self.GREEN, circle_position, self.circle_size)

        elif question_set_index == "yellow":
            pygame.draw.circle(self.main_window, self.YELLOW, circle_position, self.circle_size)

        elif question_set_index == "white":
            pygame.draw.circle(self.main_window, self.WHITE, circle_position, self.circle_size)

        # Pedals
        elif question_set_index == "left_pedal":
            pygame.draw.rect(self.main_window,
                             (253, 253, 253),
                             (50, int(self.main_window.get_height() - self.pedal_height - 50),
                              self.pedal_width,
                              self.pedal_height))

        elif question_set_index == "right_pedal":
            pygame.draw.rect(self.main_window,
                             (253, 253, 253),
                             (int(self.main_window.get_width() - self.pedal_width - 50),
                              int(self.main_window.get_height() - self.pedal_height - 50),
                              self.pedal_width,
                              self.pedal_height))

        # Sound
        elif question_set_index == "high_tone":
            self.high_tone.play(loops=0, maxtime=int(sound_duration), fade_ms=10)

        elif question_set_index == "low_tone":
            self.low_tone.play(loops=0, maxtime=int(sound_duration), fade_ms=10)

    def random_circle_position(self):
        position = [random.randint(0 + self.circle_size * 3, self.main_window.get_width() - self.circle_size * 3),
                    random.randint(0 + self.circle_size * 3, self.main_window.get_height() - self.circle_size * 3)]
        return position

    # Method that initialises recording of the answers for the upcoming test
    def record_answers(self, test_form):
        username = "Guest"
        score_id = None

        # Check if a user was given
        if self.current_user is not None:
            username = self.current_user.user_name

            # Check if the user is in the user database
            user_in_database = user_database.select_current_user(self.current_user.user_id)

            # Record answers only for users tracked in User Table
            if user_in_database is not None:
                # Connect to existing score table or create one
                user_database.create_score_table()

                # Connect to existing score table or create one
                user_database.create_answer_table()

                # Make Score Table entry for the current test and return the ID of the current score
                score_id = user_database.insert_into_score_table(
                    test_form,
                    datetime.now().strftime("%d/%m/%Y %H:%M"),
                    self.current_user.user_id)

                # Clean Score Table of any unwanted answers before recording
                user_database.delete_answers(score_id)

                return username, score_id  # ID of the score which is going to receive answers from the test
        return username, score_id  # Returns None -> answers are not being recorded

    def scan_for_pressed_buttons(self, buttons, panel_detected=False):
        # Scan for buttons only if the control panel is being used to control the test
        if panel_detected:
            white_button = buttons[0]
            yellow_button = buttons[1]
            green_button = buttons[2]
            blue_button = buttons[3]
            red_button = buttons[4]
            up_button = buttons[5]
            down_button = buttons[6]
            left_pedal = buttons[7]
            right_pedal = buttons[8]

            # Check for button pressing
            if white_button.is_pressed:
                self.pressing_button("w", pygame.K_w)
            if yellow_button.is_pressed:
                self.pressing_button("y", pygame.K_y)
            if green_button.is_pressed:
                self.pressing_button("g", pygame.K_g)
            if blue_button.is_pressed:
                self.pressing_button("b", pygame.K_b)
            if red_button.is_pressed:
                self.pressing_button("r", pygame.K_r)
            if up_button.is_pressed:
                self.pressing_button(None, pygame.K_UP)
            if down_button.is_pressed:
                self.pressing_button(None, pygame.K_DOWN)
            if left_pedal.is_pressed:
                self.pressing_button(None, pygame.K_LEFT)
            if right_pedal.is_pressed:
                self.pressing_button(None, pygame.K_RIGHT)
        else:
            pass

    # Method that starts the test
    @abstractmethod
    def run(self, phase="Instructions"):
        pass
