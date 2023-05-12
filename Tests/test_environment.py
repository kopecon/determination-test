import pygame
from pygame import VIDEORESIZE, mixer
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

    # Display parameters
    FPS_ceiling = 2000  # Frame rate celling
    
    stimulus_parameters = {'circle_size': 100, 'pedal_width': 150, 'pedal_height': 250, 'volume': 0.2}
    
    # Switch debounce time [s] - countermeasure to left pedal "Switch Bounce"
    debounce_time = 0.2  # Empirically measured time... could be around 190 ms

    # Directory to search for dependencies
    project_dir = os.path.join(os.getcwd(), os.pardir)
    tests_style_dir = f'{project_dir}/Tests/Style'

    # Pygame environment properties
    clock = None
    monitor_size = None
    main_window = None
    fullscreen = True
    sound_bank = {}
    title = None
    text = None
    instr = None
    title_pos = None
    text_pos = None
    instr_pos = None

    def __init__(self, device=None, current_user=None):
        # Current user
        self.current_user = current_user
        self.device = device
        self.test_name = ""
        self.test_info = ""  # Description of the test that is specified for each test individually
        # Style color palette
        self.color_scheme = {'GRAY': (41, 43, 45),
                             'LIGHT_GRAY': (161, 163, 165),
                             'BLACK': (0, 0, 0), 'GREEN': (7, 169, 48),
                             'WHITE': (253, 253, 253), 'BLUE': (0, 0, 179),
                             'RED': (159, 0, 27), 'YELLOW': (255, 204, 0)}

    @abstractmethod
    def __repr__(self):
        pass

    def start_pygame(self):
        """
        Initializing pygame with pygame.init() directly from the class builder causes issues
        with Kivy. Cannot reopen menu window after quiting pygame.
        This method is called in every "run()" to initialize pygame.
        """
        # Initialize Pygame
        pygame.init()

        # Define clock
        self.clock = pygame.time.Clock()

        # Get Monitor Info
        self.monitor_size = (pygame.display.Info().current_w, pygame.display.Info().current_h)

        # Set up the test window
        self.main_window = pygame.display.set_mode(self.monitor_size, pygame.FULLSCREEN)

        # Set up sound bank
        self.sound_bank = {'high_tone': mixer.Sound(f'{self.tests_style_dir}/Sounds/High.wav'),
                           'low_tone': mixer.Sound(f'{self.tests_style_dir}/Sounds/Low.wav')}
        self.sound_bank['high_tone'].set_volume(self.stimulus_parameters['volume'])
        self.sound_bank['low_tone'].set_volume(self.stimulus_parameters['volume'])

        # Text properties [font, font size]
        title = [f'{self.tests_style_dir}/Fonts/Handgotn.ttf', 70]
        text = [f'{self.tests_style_dir}/Fonts/BebasNeue Book.ttf', 55]
        instr = [f'{self.tests_style_dir}/Fonts/BebasNeue Regular.ttf', 60]

        # Define text style
        self.title = pygame.freetype.Font(title[0], title[1])
        self.title_pos = (100, self.monitor_size[1] / 6 - title[1] * 1.5)
        self.text = pygame.freetype.Font(text[0], text[1])
        self.text_pos = (150, self.monitor_size[1] / 3 - text[1] * 1.5)
        self.instr = pygame.freetype.Font(instr[0], instr[1])
        self.instr_pos = (150, self.monitor_size[1] / 1.05 - instr[1] * 1.5)

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
        buttons = {'white_button': None, 'yellow_button': None, 'green_button': None, 'blue_button': None,
                   'red_button': None, 'up_button': None, 'down_button': None, 'left_pedal': None, 'right_pedal': None}

        # User chose to use control pane to control the test
        if self.device is not None and self.device.device_type == "CONTROL PANEL":
            # Protect if panel IP address is not found
            try:
                # Create a connection to the Raspberry Pi remote GPIO
                factory = PiGPIOFactory(host=self.device.device_ip)

                # Confirm connection with the panel
                panel_detected = True

                # Declare buttons and pedals based on their hardware representation
                buttons['white_button'] = Button(18, pin_factory=factory, pull_up=False)
                buttons['yellow_button'] = Button(14, pin_factory=factory, pull_up=False)
                buttons['green_button'] = Button(15, pin_factory=factory, pull_up=False)
                buttons['blue_button'] = Button(22, pin_factory=factory, pull_up=False)
                buttons['red_button'] = Button(27, pin_factory=factory, pull_up=False)
                buttons['up_button'] = Button(23, pin_factory=factory, pull_up=False)
                buttons['down_button'] = Button(17, pin_factory=factory, pull_up=False)
                buttons['left_pedal'] = Button(24, pin_factory=factory, pull_up=False)
                buttons['right_pedal'] = Button(25, pin_factory=factory, pull_up=False)

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

    def scan_for_pressed_buttons(self, buttons, panel_detected=False):
        # Scan for buttons only if the control panel is being used to control the test
        if panel_detected:
            white_button = buttons['white_button']
            yellow_button = buttons['yellow_button']
            green_button = buttons['green_button']
            blue_button = buttons['blue_button']
            red_button = buttons['red_button']
            up_button = buttons['up_button']
            down_button = buttons['down_button']
            left_pedal = buttons['left_pedal']
            right_pedal = buttons['right_pedal']

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

    # Define stimulus which is being presented during the test
    def stimulus(self, stimulus_type, circle_position, sound_duration=1500):

        # Color Circles
        if stimulus_type in ['WHITE', 'GREEN', 'RED', 'YELLOW', 'BLUE']:
            pygame.draw.circle(
                self.main_window,
                self.color_scheme[stimulus_type],
                circle_position,
                self.stimulus_parameters['circle_size'])

        # Pedals
        elif stimulus_type == "left_pedal":
            pygame.draw.rect(self.main_window,
                             (253, 253, 253),
                             (50, int(self.main_window.get_height() - self.stimulus_parameters['pedal_height'] - 50),
                              self.stimulus_parameters['pedal_width'],
                              self.stimulus_parameters['pedal_height']))

        elif stimulus_type == "right_pedal":
            pygame.draw.rect(self.main_window,
                             (253, 253, 253),
                             (int(self.main_window.get_width() - self.stimulus_parameters['pedal_width'] - 50),
                              int(self.main_window.get_height() - self.stimulus_parameters['pedal_height'] - 50),
                              self.stimulus_parameters['pedal_width'],
                              self.stimulus_parameters['pedal_height']))

        # Sound
        elif stimulus_type in ['high_tone', 'low_tone']:
            self.sound_bank[stimulus_type].play(loops=0, maxtime=int(sound_duration), fade_ms=10)

    def random_circle_position(self):
        position = [random.randint(0 + self.stimulus_parameters['circle_size'] * 3,
                                   self.main_window.get_width() - self.stimulus_parameters['circle_size'] * 3),
                    random.randint(0 + self.stimulus_parameters['circle_size'] * 3,
                                   self.main_window.get_height() - self.stimulus_parameters['circle_size'] * 3)]
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

    def exit(self, phase, event, score_id):
        """
        Method that quits the test environment if "ESC" key or "close" button is pressed.
        This method also handles fullscreen swapping.
        :param phase: Keeps trak in which phase we quit to decide if it should store recorded data or not.
        :param event: Feeds in what buttons/keys are being pressed.
        :param score_id: Deletes this score if quit outside exit phase.
        :return: True if the test is being quited.
        """

        # Closing the window by pressing X button on the window screen
        if event.type == pygame.QUIT:
            # Delete unfinished test score
            if not phase == "Exit" and score_id is not None:
                user_database.delete_score(score_id)

            pygame.quit()
            return True

        # Closing the window by pressing ESC
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Delete unfinished test score
                if not phase == "Exit" and score_id is not None:
                    user_database.delete_score(score_id)
                pygame.quit()
                return True

        # Update screen size when manually resizing window
        if event.type == VIDEORESIZE:
            if not self.fullscreen:
                self.main_window = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

        # Enter Fullscreen when pressing "f" on the keyboard
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_f:
                self.fullscreen = not self.fullscreen
                if self.fullscreen:
                    self.main_window = pygame.display.set_mode(self.monitor_size, pygame.FULLSCREEN)

                else:
                    self.main_window = pygame.display.set_mode(
                        (int(self.main_window.get_width() - 500),
                         int(self.main_window.get_height()) - 500),
                        pygame.RESIZABLE)

    # Method that starts the test
    @abstractmethod
    def run(self, phase="Instructions"):
        pass
