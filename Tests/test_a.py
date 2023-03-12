import pygame
from pygame import mixer, VIDEORESIZE, freetype
from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import Button
from datetime import datetime
import random
import time
import statistics
import os

# -------------------------   Import Custom Program Code

from Database import user_database
from Tests import question_set

# ------------------------------   Adjustable parameters


# Display parameters
FPS = 2000  # Frame rate celling

# Test parameters
test_duration = 240000 / 20  # Test duration in ms (4 min by default)
volume = 0.2  # Volume of the sound stimulus - Values from 0 to 1 (1 = Max volume) [%]

# Stimulus parameters
circle_size = 100  # Radius of the color circle stimulus [pixel]
pedal_width = 150  # Width of the pedal symbol [pixel]
pedal_height = 250  # Height of the pedal symbol [pixel]

# Directory to search for dependencies
project_dir = os.path.join(os.getcwd(), os.pardir)
tests_style_dir = f'{project_dir}/Tests/Style'

# Text properties
font_title = f'{tests_style_dir}/Fonts/Handgotn.ttf'
title_font_size = 70
font_text = f'{tests_style_dir}/Fonts/BebasNeue Book.ttf'
text_font_size = 55
font_instr = f'{tests_style_dir}/Fonts/BebasNeue Regular.ttf'
instr_font_size = 60

# --------------------   Used variables (not adjustable)

GRAY = (41, 43, 45)
LIGHT_GRAY = (GRAY[0] + 120, GRAY[0] + 120, GRAY[0] + 120)
BLACK = (0, 0, 0)
GREEN = (7, 169, 48)
WHITE = (253, 253, 253)
BLUE = (0, 0, 179)
RED = (159, 0, 27)
YELLOW = (255, 204, 0)
color_types = [GREEN, BLUE, RED, YELLOW, WHITE]
# Test title
title = "DETERMINATION TEST - FORM A - ADAPTIVE"


# ------------------------------------------   Functions
# Define a Function to call test program in the menu app
class TestProgramFormA:
    def __init__(self):
        # Predefine buttons
        self.white_button = None
        self.yellow_button = None
        self.green_button = None
        self.blue_button = None
        self.red_button = None
        self.up_button = None
        self.down_button = None
        self.left_pedal = None
        self.right_pedal = None

        # Predefine panel detection
        self.panel_detected = False
        # Predefined state of keyboard simulation event
        self.button_event = None
        # Switch debounce time [s] - empirically measured time (countermeasure to left pedal "Switch Bounce")
        self.debounce_time = 0.2  # Could be around 190 ms

    # Simulate keyboard press with GPIO Button
    def pressing_button(self, unicode, represented_key):
        self.button_event = pygame.event.Event(
            pygame.KEYDOWN,
            unicode=unicode,
            key=represented_key,
            mod=pygame.KMOD_NONE
        )
        pygame.event.post(self.button_event)

    # Define Stimulus Type
    def stimulus(self, question_set_index):

        # Color Circles
        if question_set_index == "red":
            pygame.draw.circle(self.main_window, RED, self.circle_position, circle_size)
            self.tone_played = False

        elif question_set_index == "blue":
            pygame.draw.circle(self.main_window, BLUE, self.circle_position, circle_size)
            self.tone_played = False

        elif question_set_index == "green":
            pygame.draw.circle(self.main_window, GREEN, self.circle_position, circle_size)
            self.tone_played = False

        elif question_set_index == "yellow":
            pygame.draw.circle(self.main_window, YELLOW, self.circle_position, circle_size)
            self.tone_played = False

        elif question_set_index == "white":
            pygame.draw.circle(self.main_window, WHITE, self.circle_position, circle_size)
            self.tone_played = False

        # Pedals
        elif question_set_index == "left_pedal":
            pygame.draw.rect(self.main_window,
                             (253, 253, 253),
                             (50, int(self.main_window.get_height() - pedal_height - 50),
                              pedal_width,
                              pedal_height))
            self.tone_played = False

        elif question_set_index == "right_pedal":
            pygame.draw.rect(self.main_window,
                             (253, 253, 253),
                             (int(self.main_window.get_width() - pedal_width - 50),
                              int(self.main_window.get_height() - pedal_height - 50),
                              pedal_width,
                              pedal_height))
            self.tone_played = False

        # Tone
        elif question_set_index == "high_tone":
            # prevent looping of the sound
            if not self.tone_played:
                self.high_tone.play(loops=0, maxtime=int(self.stimulus_adaptive_delay_ms), fade_ms=10)
                self.tone_played = True

        elif question_set_index == "low_tone":
            # prevent looping of the sound
            if not self.tone_played:
                self.low_tone.play(loops=0, maxtime=int(self.stimulus_adaptive_delay_ms), fade_ms=10)
                self.tone_played = True

    # Method that starts the test
    def test_program_run(self, user, input_device, device_ip):
        # Check for selected device
        if input_device == "Control panel":
            # Protect if panel IP address is not found
            try:
                # Create a connection to the Raspberry Pi remote GPIO
                factory = PiGPIOFactory(host=device_ip)

                # Define buttons
                self.white_button = Button(18, pin_factory=factory, pull_up=False)
                self.yellow_button = Button(14, pin_factory=factory, pull_up=False)
                self.green_button = Button(15, pin_factory=factory, pull_up=False)
                self.blue_button = Button(22, pin_factory=factory, pull_up=False)
                self.red_button = Button(27, pin_factory=factory, pull_up=False)
                self.up_button = Button(23, pin_factory=factory, pull_up=False)
                self.down_button = Button(17, pin_factory=factory, pull_up=False)
                self.left_pedal = Button(24, pin_factory=factory, pull_up=False)
                self.right_pedal = Button(25, pin_factory=factory, pull_up=False)
                self.button_event = None
                self.panel_detected = True

            # Return to menu if panel is not found
            except OSError:
                self.panel_detected = False

                return self.panel_detected

        # Used Variables
        user_data = user_database.select_current_user(user)
        user_name = f"{user_data[2]} {user_data[3]}"
        previous_stimulus_time_ms = 0
        reset_respond_time_ms = 0
        stimulus_time = 0
        current_script_time_ms = 0
        answered = False
        flip = True
        self.phase = "Instruction"

        # Measured variables
        self.response_time_ns_array = []
        self.adaptive_response_array = [1078, 1078, 1078, 1078, 1078, 1078, 1078, 1078]

        # Start with first stimulus from the list
        self.stimulus_index = 0

        # Start in fullscreen
        self.fullscreen = True

        # --------------------------   Set up the pygame
        # Initialize Pygame
        pygame.init()

        # Get Monitor Info
        monitor_size = [pygame.display.Info().current_w, pygame.display.Info().current_h]
        window_width = monitor_size[0]
        window_height = monitor_size[1]

        # Set up the window
        self.main_window = pygame.display.set_mode((window_width, window_height), pygame.FULLSCREEN)
        pygame.display.set_caption("DT Test Form A")

        self.main_window.fill(GRAY)

        # Set up sound bank
        self.high_tone = mixer.Sound(f'{tests_style_dir}/Sounds/High.wav')
        self.high_tone.set_volume(volume)
        self.low_tone = mixer.Sound(f'{tests_style_dir}/Sounds/Low.wav')
        self.low_tone.set_volume(volume)
        self.tone_played = False
        self.answer_type = None

        # Text properties
        self.font_title = pygame.freetype.Font(font_title, 70)
        title_pos = (100, window_height / 6 - title_font_size * 1.5)
        self.font_text = pygame.freetype.Font(font_text, 70)
        text_pos = (150, window_height / 3 - text_font_size * 1.5)
        self.font_instr = pygame.freetype.Font(font_instr, 70)
        instr_pos = (150, window_height / 1.05 - instr_font_size * 1.5)

        # Define clock
        self.clock = pygame.time.Clock()

        # Start circle at random position
        self.circle_position = [random.randint(0 + circle_size * 3, self.main_window.get_width() - circle_size * 3),
                                random.randint(0 + circle_size * 3, self.main_window.get_height() - circle_size * 3)]

        # Connect to existing score table or create one
        user_database.create_score_table()

        # Connect to existing score table or create one
        user_database.create_answer_table()

        # Make Score Table entry for current test
        current_score_id = user_database.insert_into_score_table("A",
                                                                 datetime.now().strftime("%d/%m/%Y %H:%M"),
                                                                 user
                                                                 )
        # Clean Score Table for current test of any unwanted answers

        user_database.delete_answer(current_score_id)

        # Main while loop
        while True:
            # Use GPIO Button class only if the panel is detected
            if self.panel_detected:
                # Check for button pressing
                if self.white_button.is_pressed:
                    self.pressing_button("w", pygame.K_w)
                if self.yellow_button.is_pressed:
                    self.pressing_button("y", pygame.K_y)
                if self.green_button.is_pressed:
                    self.pressing_button("g", pygame.K_g)
                if self.blue_button.is_pressed:
                    self.pressing_button("b", pygame.K_b)
                if self.red_button.is_pressed:
                    self.pressing_button("r", pygame.K_r)
                if self.up_button.is_pressed:
                    self.pressing_button(None, pygame.K_UP)
                if self.down_button.is_pressed:
                    self.pressing_button(None, pygame.K_DOWN)
                if self.left_pedal.is_pressed:
                    self.pressing_button(None, pygame.K_LEFT)
                if self.right_pedal.is_pressed:
                    self.pressing_button(None, pygame.K_RIGHT)

            # Calculate time delay for next stimulus from last 8 reaction times
            self.last_8_responses = self.adaptive_response_array[-8:]
            self.stimulus_adaptive_delay_ms = statistics.mean(self.last_8_responses)

            # Finish test after time runs out
            if current_script_time_ms >= test_duration and stimulus_time == 0 and flip:
                flip = False

                self.main_window.fill(GRAY)
                pygame.display.flip()

                text_text = "Loading..."
                title_surface = self.font_text.render(
                    text=text_text,
                    fgcolor=LIGHT_GRAY,
                    size=title_font_size
                )
                self.main_window.blit(title_surface[0], title_surface[1].move(window_width * 0.44, text_pos[1] * 1.5))
                pygame.display.flip()

                time.sleep(2)

                self.main_window.fill(GRAY)
                pygame.display.flip()

                self.phase = "Exit"

            # Event loop
            for event in pygame.event.get():

                # Closing the window by pressing X button on the window screen
                if event.type == pygame.QUIT:
                    # Delete unfinished test score
                    if not self.phase == "Exit":
                        user_database.delete_score(current_score_id)

                    pygame.quit()
                    return

                # Closing the window by pressing ESC
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # Delete unfinished test score
                        if not self.phase == "Exit":
                            user_database.delete_score(current_score_id)
                        pygame.quit()
                        return

                # Update screen size when manually resizing window
                if event.type == VIDEORESIZE:
                    if not self.fullscreen:
                        self.main_window = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

                # Enter Fullscreen when pressing "f" on the keyboard
                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_f:
                        self.fullscreen = not self.fullscreen
                        if self.fullscreen:
                            self.main_window = pygame.display.set_mode(monitor_size, pygame.FULLSCREEN)

                        else:
                            self.main_window = pygame.display.set_mode(
                                (int(self.main_window.get_width() - 500),
                                 int(self.main_window.get_height()) - 500),
                                pygame.RESIZABLE)

                # Scan for input (button/key)
                if event.type == pygame.KEYDOWN and not event.key == pygame.K_f:
                    # Start test by pressing any button/key
                    if self.phase == "Instruction":
                        self.phase = "Test"
                        self.main_window.fill(GRAY)
                        pygame.display.flip()
                        time.sleep(self.stimulus_adaptive_delay_ms / 1000)
                        # Clear Event Queue to prevent from reacting before stimulus shown
                        pygame.event.clear()
                        # Get epoch time
                        self.epoch_time = time.time_ns()

                    # Catch reaction
                    elif self.phase == "Test":

                        self.main_window.fill(GRAY)
                        pygame.display.flip()

                        pygame.mixer.pause()

                        # Get response time
                        press_time_ns = (time.time_ns() - self.epoch_time)
                        self.response_time_ns = press_time_ns - reset_respond_time_ms * 1000000

                        # Use the first response time per stimulus to calculate stimulus adaptive delay
                        if not answered:
                            self.response_time_ns_array.append(self.response_time_ns / 1000000)

                        # Check for answer properties and insert them to answer table
                        # Correct Answer
                        if event.key == question_set.answer_set[self.stimulus_index] \
                                and not answered:
                            # Insert correct answer in to answer table
                            self.answer_type = user_database.insert_into_answer_table(
                                question_set.question_set[self.stimulus_index],
                                pygame.key.name(event.key),
                                "Correct",
                                current_script_time_ms / 1000,
                                self.response_time_ns / 1000000,
                                current_score_id
                            )

                            # Add measured reaction time to the calculation of the next stimulus delay time
                            self.adaptive_response_array.append(self.response_time_ns_array[-1])

                        # Incorrect Answer
                        elif not event.key == question_set.answer_set[self.stimulus_index] \
                                and not event.key == question_set.answer_set[self.stimulus_index - 1] \
                                and not answered:

                            # Insert incorrect answer in to answer table
                            self.answer_type = user_database.insert_into_answer_table(
                                question_set.question_set[self.stimulus_index],
                                pygame.key.name(event.key),
                                "Incorrect",
                                current_script_time_ms / 1000,
                                self.response_time_ns / 1000000,
                                current_score_id
                            )

                            # Add doubled current stimulus delay time to the calculation of the next stimulus delay time
                            self.adaptive_response_array.append(self.stimulus_adaptive_delay_ms * 2)

                        # Late Answer
                        elif not event.key == question_set.answer_set[self.stimulus_index] \
                                and event.key == question_set.answer_set[self.stimulus_index - 1] \
                                and not answered:

                            if self.answer_type == "Missed":
                                # Update missed answer to late answer in answer table
                                self.answer_type = user_database.update_answer(
                                    question_set.question_set[self.stimulus_index - 1],
                                    pygame.key.name(event.key),
                                    "Late",
                                    current_script_time_ms / 1000,
                                    self.response_time_ns / 1000000,
                                    self.stimulus_index
                                )

                            # Add doubled current stimulus delay time to the calculation of the next stimulus delay time
                            self.adaptive_response_array.append(self.stimulus_adaptive_delay_ms * 2)

                        # Repeated Answer
                        elif answered:

                            # Insert repeated answer in to answer table as incorrect answer
                            self.answer_type = user_database.insert_into_answer_table(
                                "Repeated Input",
                                pygame.key.name(event.key),
                                "Incorrect",
                                current_script_time_ms / 1000 / 1000,
                                self.response_time_ns / 1000000,
                                current_score_id
                            )
                            # Prevent over clogging of the event queue by spamming answers
                            pygame.event.clear()

                        answered = True

                        # Debounce GPIO input (It takes 200 ms for another input to be recognized)
                        time.sleep(self.debounce_time)

                    # Return to the menu by pressing any button/key if in the "Exit screen"
                    elif self.phase == "Exit":
                        pygame.quit()
                        return

            # Display START message
            if self.phase == "Instruction":

                text_title = title
                title_surface = self.font_title.render(
                    text=text_title,
                    fgcolor=LIGHT_GRAY,
                    size=title_font_size
                )
                self.main_window.blit(title_surface[0], title_surface[1].move(title_pos))

                text_text = f"User:       {user_name}"
                text_surface = self.font_text.render(
                    text=text_text,
                    fgcolor=LIGHT_GRAY,
                    size=text_font_size
                )
                self.main_window.blit(text_surface[0], text_surface[1].move(text_pos))

                text_text = "Following test is being measured."
                text_surface = self.font_text.render(
                    text=text_text,
                    fgcolor=LIGHT_GRAY,
                    size=text_font_size
                )
                self.main_window.blit(
                    text_surface[0],
                    text_surface[1].move(text_pos[0], text_pos[1] + text_font_size * 2.5)
                )

                text_text = "Only one stimulus is being presented at a time."
                text_surface = self.font_text.render(
                    text=text_text,
                    fgcolor=LIGHT_GRAY,
                    size=text_font_size
                )
                self.main_window.blit(
                    text_surface[0],
                    text_surface[1].move(text_pos[0], text_pos[1] + text_font_size * 3.75)
                )

                text_text = "React as fast as possible."
                text_surface = self.font_text.render(
                    text=text_text,
                    fgcolor=LIGHT_GRAY,
                    size=text_font_size
                )
                self.main_window.blit(
                    text_surface[0],
                    text_surface[1].move(text_pos[0], text_pos[1] + text_font_size * 5)
                )

                text_text = "Tempo of the task assignment is changing during the test."
                text_surface = self.font_text.render(
                    text=text_text,
                    fgcolor=LIGHT_GRAY,
                    size=text_font_size
                )
                self.main_window.blit(
                    text_surface[0],
                    text_surface[1].move(text_pos[0], text_pos[1] + text_font_size * 6.25)
                )

                text_text_5 = f"Test duration:      {test_duration / 60 / 1000} min"
                middle_text_text_5_surface = self.font_text.render(
                    text=text_text_5,
                    fgcolor=LIGHT_GRAY,
                    size=text_font_size
                )
                self.main_window.blit(
                    middle_text_text_5_surface[0],
                    middle_text_text_5_surface[1].move(text_pos[0], text_pos[1] + text_font_size * 8.75)
                )

                text_instr = "PRESS ANY BUTTON TO BEGIN"
                instr_surface = self.font_instr.render(
                    text=text_instr,
                    fgcolor=LIGHT_GRAY,
                    size=instr_font_size
                )
                self.main_window.blit(
                    instr_surface[0],
                    instr_surface[1].move(text_pos[0] + window_width * 0.6, instr_pos[1])
                )

            # Start the test
            elif self.phase == "Test":
                # Set "time zero" when running the test
                current_script_time_ms = (time.time_ns() - self.epoch_time) / 1000000

                # Display stimulus
                if not answered:
                    self.main_window.fill(GRAY)
                    question_set_index = question_set.question_set[self.stimulus_index]
                    self.stimulus(question_set_index)
                    pygame.display.flip()

                # Get individual time per stimulus
                stimulus_time = current_script_time_ms - previous_stimulus_time_ms

                # End of current stimulus
                if stimulus_time >= self.stimulus_adaptive_delay_ms:
                    # Check for missed answers
                    if not answered:
                        # Double the last stimulus delay to calculate next stimulus delay
                        self.adaptive_response_array.append(self.stimulus_adaptive_delay_ms * 2)

                        # Insert missed answer in to answer table
                        self.answer_type = user_database.insert_into_answer_table(
                            question_set.question_set[self.stimulus_index],
                            None,
                            "Missed",
                            current_script_time_ms / 1000,
                            0,
                            current_score_id
                        )

                    # Prepare new random position
                    self.circle_position = [
                        random.randint(
                            0 + circle_size * 3,
                            self.main_window.get_width() - circle_size * 3),
                        random.randint(0 + circle_size * 3,
                                       self.main_window.get_height() - circle_size * 3)]

                    # Clear Event Queue to prevent from reacting before stimulus shown
                    pygame.event.clear()

                    # Next stimulus
                    if self.stimulus_index < len(question_set.question_set) - 1:
                        self.stimulus_index += 1
                    else:
                        self.stimulus_index = 0

                    # Reset stimulus time
                    previous_stimulus_time_ms = (time.time_ns() - self.epoch_time) / 1000000
                    # Reset reaction time if answered
                    if answered:
                        reset_respond_time_ms = previous_stimulus_time_ms
                    stimulus_time = 0

                    answered = False

            # Display EXIT message
            elif self.phase == "Exit":

                text_title = title
                title_surface = self.font_title.render(
                    text=text_title,
                    fgcolor=LIGHT_GRAY,
                    size=title_font_size
                )
                self.main_window.blit(title_surface[0], title_surface[1].move(title_pos))

                text_text = "The test is finished."
                text_surface = self.font_text.render(
                    text=text_text,
                    fgcolor=LIGHT_GRAY,
                    size=text_font_size
                )
                self.main_window.blit(text_surface[0], text_surface[1].move(text_pos))

                text_text = f"Test ID:        {current_score_id}"
                text_surface = self.font_text.render(
                    text=text_text,
                    fgcolor=LIGHT_GRAY,
                    size=text_font_size
                )
                self.main_window.blit(
                    text_surface[0],
                    text_surface[1].move(text_pos[0], text_pos[1] + text_font_size * 2.5)
                )

                text_text = f"The results are available at {user_name}'s profile."
                text_surface = self.font_text.render(
                    text=text_text,
                    fgcolor=LIGHT_GRAY,
                    size=text_font_size
                )
                self.main_window.blit(
                    text_surface[0],
                    text_surface[1].move(text_pos[0], text_pos[1] + text_font_size * 3.75)
                )

                text_instr = "PRESS ANY BUTTON TO RETURN TO THE MENU"
                instr_surface = self.font_instr.render(
                    text=text_instr,
                    fgcolor=LIGHT_GRAY,
                    size=instr_font_size
                )
                self.main_window.blit(
                    instr_surface[0],
                    instr_surface[1].move(text_pos[0] + window_width * 0.5, instr_pos[1])
                )
                pygame.display.flip()

            # While loop routine
            pygame.display.update()
            self.clock.tick_busy_loop(FPS)  # For more accurate display timer


if __name__ == '__main__':
    print(pygame.get_sdl_version())
    training = TestProgramFormA()
    training.test_program_run(1, 'keyboard', '16543')
