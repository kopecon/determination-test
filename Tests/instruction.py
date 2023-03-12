import pygame
from pygame import mixer, VIDEORESIZE, freetype
from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import Button
import time
import os


# -----------------------------------------------------------------------------------------   Import Custom Program Code
from Tests import training

# ----------------------------------------------------------------------------------------------   Adjustable parameters
# Display parameters
background_color = (0, 0, 0)  # Set background color (Black by default)
FPS = 60  # Frame rate celling (240 FPS -> completing once cycle of "main while loop" takes about 4.1666 ms)

# Test parameters
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

# ------------------------------------------------------------------------------------   Used variables (not adjustable)
GRAY = (41, 43, 45)
LIGHT_GRAY = (GRAY[0] + 120, GRAY[0] + 120, GRAY[0] + 120)
BLACK = (0, 0, 0)
GREEN = (7, 169, 48)
WHITE = (253, 253, 253)
BLUE = (0, 0, 179)
RED = (159, 0, 27)
YELLOW = (255, 204, 0)
color_types = [GREEN, BLUE, RED, YELLOW, WHITE]

# Instructions title
title = "DETERMINATION TEST - INSTRUCTIONS"


# ----------------------------------------------------------------------------------------------------------   Functions
# Define a Function to call test program in the menu app
# noinspection PyGlobalUndefined
class TestInstructions:
    def __init__(self):
        # Predefine buttons
        self.panel_detected = False
        self.white_button = None
        self.yellow_button = None
        self.green_button = None
        self.blue_button = None
        self.red_button = None
        self.up_button = None
        self.down_button = None
        self.left_pedal = None
        self.right_pedal = None

        # ------------------------------------------------------------------------------------------   Set up the pygame
        # Initialize Pygame
        pygame.init()

        # Set up sound bank
        self.high_tone = mixer.Sound(f'{tests_style_dir}/Sounds/High.wav')
        self.high_tone.set_volume(volume)
        self.low_tone = mixer.Sound(f'{tests_style_dir}/Sounds/Low.wav')
        self.low_tone.set_volume(volume)

        # Define clock
        self.clock = pygame.time.Clock()

        """
        Instruction phase:
            1 ... First Checkpoint
            A ... Color Stimulus instructions
            2 ... Second Checkpoint
            B ... Pedal instructions
            3 ... Third Checkpoint
            C ... Tones instructions
        """
        self.phase = 1
        self.up_arrow_scale_factor = (100, 100)
        self.down_arrow_scale_factor = (100, 100)

        self.instructions_color_stimulus_question_set = [
            "white",
            "yellow",
            "blue",
            "green",
            "red"
        ]

        self.instructions_color_stimulus_answer_set = [
            pygame.K_w,
            pygame.K_y,
            pygame.K_b,
            pygame.K_g,
            pygame.K_r
        ]

        self.instructions_pedal_question_set = [
            "Left Pedal",
            "Right Pedal",
            "Left Pedal",
            "Right Pedal",
        ]

        self.instructions_pedal_answer_set = [
            pygame.K_LEFT,
            pygame.K_RIGHT,
            pygame.K_LEFT,
            pygame.K_RIGHT,
        ]

        self.instructions_tone_question_set = [
            "Up Arrow",
            "Down Arrow",
            "High Tone",
            "Low Tone",
            "High Tone",
            "Low Tone",
        ]

        self.instructions_tone_answer_set = [
            pygame.K_UP,
            pygame.K_DOWN,
            pygame.K_UP,
            pygame.K_DOWN,
            pygame.K_UP,
            pygame.K_DOWN,
        ]

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
    def stimulus(self, selected_question):

        # Color Circles
        if selected_question == "red":
            pygame.draw.circle(self.main_window, RED, self.circle_position, circle_size)
            self.tone_played = False

        elif selected_question == "blue":
            pygame.draw.circle(self.main_window, BLUE, self.circle_position, circle_size)
            self.tone_played = False

        elif selected_question == "green":
            pygame.draw.circle(self.main_window, GREEN, self.circle_position, circle_size)
            self.tone_played = False

        elif selected_question == "yellow":
            pygame.draw.circle(self.main_window, YELLOW, self.circle_position, circle_size)
            self.tone_played = False

        elif selected_question == "white":
            pygame.draw.circle(self.main_window, WHITE, self.circle_position, circle_size)
            self.tone_played = False

        # Pedals
        elif selected_question == "Left Pedal":
            pygame.draw.rect(self.main_window,
                             WHITE,
                             (50, int(self.main_window.get_height() - pedal_height - 50),
                              pedal_width,
                              pedal_height))
            self.tone_played = False

        elif selected_question == "Right Pedal":
            pygame.draw.rect(self.main_window,
                             WHITE,
                             (int(self.main_window.get_width() - pedal_width - 50),
                              int(self.main_window.get_height() - pedal_height - 50),
                              pedal_width,
                              pedal_height))
            self.tone_played = False

        elif selected_question == "High Tone":
            self.high_tone.play(loops=0, fade_ms=10)

        elif selected_question == "Low Tone":
            self.low_tone.play(loops=0, fade_ms=10)

        elif selected_question == "Up Arrow":
            self.up_arrow_surface = pygame.Surface((200, 200))
            self.up_arrow_surface.fill(GRAY)
            pygame.draw.circle(self.up_arrow_surface, (GRAY[0] - 28, GRAY[1] - 28, GRAY[2] - 28), (100, 100), 100)
            pygame.draw.polygon(self.up_arrow_surface, WHITE, (
                (90, 160),
                (90, 100),
                (70, 100),
                (100, 40),
                (130, 100),
                (110, 100),
                (110, 160)
            ))
            scaled_arrow = pygame.transform.smoothscale(self.up_arrow_surface, self.up_arrow_scale_factor)
            up_arrow_rect = scaled_arrow.get_rect(center=(
                self.main_window.get_width()/2,
                self.main_window.get_height()/2 - 100)
            )
            self.main_window.blit(scaled_arrow, up_arrow_rect)

        elif selected_question == "Down Arrow":
            scaled_arrow = pygame.transform.smoothscale(self.up_arrow_surface, self.down_arrow_scale_factor)
            down_arrow = pygame.transform.rotate(scaled_arrow, 180)
            down_arrow_rect = scaled_arrow.get_rect(center=(
                self.main_window.get_width() / 2,
                self.main_window.get_height() / 2 + 100)
            )
            self.main_window.blit(down_arrow, down_arrow_rect)

    def test_instructions_run(self, input_device, device_ip):
        # Check for selected device
        if input_device == "Control panel":
            try:
                # Create a connection to the Raspberry Pi remote GPIO
                factory = PiGPIOFactory(host=device_ip)
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
            except OSError:
                self.panel_detected = False
                return self.panel_detected

        # Start at stimulus_index 0
        self.stimulus_index = 0

        # Start in fullscreen
        self.fullscreen = True

        # Get Monitor Info
        monitor_size = [pygame.display.Info().current_w, pygame.display.Info().current_h]
        window_width = monitor_size[0]
        window_height = monitor_size[1]

        # Text properties
        self.font_title = pygame.freetype.Font(font_title, 70)
        title_pos = (100, window_height / 6 - title_font_size * 1.5)
        self.font_text = pygame.freetype.Font(font_text, 70)
        text_pos = (150, window_height / 3 - text_font_size * 1.5)
        self.font_instr = pygame.freetype.Font(font_instr, 70)
        instr_pos = (150, window_height / 1.05 - instr_font_size * 1.5)

        # Set up the window
        self.main_window = pygame.display.set_mode((window_width, window_height), pygame.FULLSCREEN)
        pygame.display.set_caption("DT Test Instructions")
        self.main_window.fill(background_color)

        self.circle_position = [self.main_window.get_width() / 2, self.main_window.get_height() / 2]

        # Main While loop
        while True:
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

            # Prevent over exceeding list limit
            try:
                self.color_stimulus_question_set_index = self.instructions_color_stimulus_question_set[
                    self.stimulus_index]
                self.pedal_question_set_index = self.instructions_pedal_question_set[self.stimulus_index]
                self.tone_question_set_index = self.instructions_tone_question_set[self.stimulus_index]
            except IndexError:
                pass

            for event in pygame.event.get():

                # Closing the window by pressing X button on the window screen
                if event.type == pygame.QUIT:
                    self.stimulus_index = 0
                    pygame.quit()
                    return True

                # Closing the window by pressing ESC
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.stimulus_index = 0
                        pygame.quit()
                        return True

                # Update screen size when manually resizing window
                if event.type == VIDEORESIZE:
                    if not self.fullscreen:
                        self.main_window = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

                # Enter Fullscreen when pressing "f"
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

                # Catch reaction
                if event.type == pygame.KEYDOWN and not event.key == pygame.K_f:
                    # First Checkpoint
                    if self.phase == 1:
                        self.stimulus_index = 0
                        self.phase = "A"
                        self.main_window.fill(GRAY)
                        pygame.display.flip()
                        time.sleep(0.5)

                    # Color Stimulus Instructions
                    elif self.phase == "A" \
                            and event.key == self.instructions_color_stimulus_answer_set[self.stimulus_index]:
                        if self.stimulus_index < len(self.instructions_color_stimulus_question_set) - 1:
                            self.stimulus_index += 1
                            self.main_window.fill(GRAY)
                            pygame.display.flip()
                            time.sleep(0.25)
                        else:
                            self.phase = 2
                            self.stimulus_index = 0
                            self.main_window.fill(GRAY)
                            pygame.display.flip()
                            time.sleep(0.25)

                    # Second Checkpoint
                    elif self.phase == 2:
                        self.phase = "B"
                        self.main_window.fill(GRAY)
                        pygame.display.flip()
                        time.sleep(0.5)

                    # Pedals Instructions
                    elif self.phase == "B" \
                            and event.key == self.instructions_pedal_answer_set[self.stimulus_index]:
                        if self.stimulus_index < len(self.instructions_pedal_question_set) - 1:
                            self.stimulus_index += 1
                            self.main_window.fill(GRAY)
                            pygame.display.flip()
                            time.sleep(0.25)
                        else:
                            self.stimulus_index = 0
                            self.phase = 3
                            self.main_window.fill(GRAY)
                            pygame.display.flip()
                            time.sleep(0.25)

                    # Third Checkpoint
                    elif self.phase == 3:
                        self.stimulus_index = 0
                        self.phase = "C"
                        self.main_window.fill(GRAY)
                        pygame.display.flip()
                        time.sleep(0.5)

                    # Tone Instructions
                    elif self.phase == "C":
                        if event.key == pygame.K_UP:
                            TestInstructions().stimulus("High Tone")
                        elif event.key == pygame.K_DOWN:
                            TestInstructions().stimulus("Low Tone")
                        elif event.key == pygame.K_w:
                            self.stimulus_index = 0
                            result = training.TestTraining().test_training_program_run(input_device, device_ip)
                            if result == "Success":
                                return "Success"
                            else:
                                self.phase = 1

            # First Checkpoint Message
            if self.phase == 1:
                self.main_window.fill(GRAY)
                text_title = title
                title_surface = self.font_title.render(
                    text=text_title,
                    fgcolor=LIGHT_GRAY,
                    size=title_font_size
                )
                self.main_window.blit(title_surface[0], title_surface[1].move(title_pos))

                text_instr = f"COLOR STIMULI"
                text_surface = self.font_instr.render(
                    text=text_instr,
                    fgcolor=LIGHT_GRAY,
                    size=text_font_size
                )
                self.main_window.blit(text_surface[0], text_surface[1].move(text_pos))

                text_text = "Following exercises are not being measured."
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

                text_text = "Press the button with the same color as the stimuli shown on the screen."
                text_surface = self.font_text.render(
                    text=text_text,
                    fgcolor=LIGHT_GRAY,
                    size=text_font_size
                )
                self.main_window.blit(
                    text_surface[0],
                    text_surface[1].move(text_pos[0], text_pos[1] + text_font_size * 5)
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

            # Display Color Stimulus instructions
            elif self.phase == "A":
                self.main_window.fill(GRAY)
                self.stimulus(self.color_stimulus_question_set_index)

            # Second Checkpoint Message
            elif self.phase == 2:

                self.main_window.fill(GRAY)
                text_instr = f"PEDALS"
                text_surface = self.font_instr.render(
                    text=text_instr,
                    fgcolor=LIGHT_GRAY,
                    size=text_font_size
                )
                self.main_window.blit(text_surface[0], text_surface[1].move(text_pos))

                text_text = "Following exercises are not being measured."
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

                text_text = "Press the pedal with the same position as the stimuli shown on the screen."
                text_surface = self.font_text.render(
                    text=text_text,
                    fgcolor=LIGHT_GRAY,
                    size=text_font_size
                )
                self.main_window.blit(
                    text_surface[0],
                    text_surface[1].move(text_pos[0], text_pos[1] + text_font_size * 5)
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

            # Display Pedal instructions
            elif self.phase == "B":
                self.main_window.fill(GRAY)
                self.stimulus(self.pedal_question_set_index)
                pygame.display.flip()

            # Third Checkpoint Message
            elif self.phase == 3:

                self.main_window.fill(GRAY)
                text_instr = f"ACOUSTIC STIMULI"
                text_surface = self.font_instr.render(
                    text=text_instr,
                    fgcolor=LIGHT_GRAY,
                    size=text_font_size
                )
                self.main_window.blit(text_surface[0], text_surface[1].move(text_pos))

                text_text = "Following exercises are not being measured."
                text_surface = self.font_text.render(
                    text=text_text,
                    fgcolor=LIGHT_GRAY,
                    size=text_font_size
                )
                self.main_window.blit(
                    text_surface[0],
                    text_surface[1].move(text_pos[0], text_pos[1] + text_font_size * 2.5)
                )

                text_text = "Press the buttons to hear the sound they represent."
                text_surface = self.font_text.render(
                    text=text_text,
                    fgcolor=LIGHT_GRAY,
                    size=text_font_size
                )
                self.main_window.blit(
                    text_surface[0],
                    text_surface[1].move(text_pos[0], text_pos[1] + text_font_size * 3.75)
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

            # Present Tone instructions
            elif self.phase == "C":

                self.main_window.fill(GRAY)
                self.stimulus("Up Arrow")
                self.stimulus("Down Arrow")

                text_instr = f"PRESS UP ARROW BUTTON TO HEAR THE HIGH TONE."
                instr_surface = self.font_text.render(
                    text=text_instr,
                    fgcolor=LIGHT_GRAY,
                    size=instr_font_size
                )

                self.main_window.blit(
                    instr_surface[0],
                    instr_surface[1].move(title_pos[0]+window_width*0.22, title_pos[1])
                )

                text_instr = f"PRESS DOWN ARROW BUTTON TO HEAR THE LOW TONE."
                instr_surface = self.font_text.render(
                    text=text_instr,
                    fgcolor=LIGHT_GRAY,
                    size=instr_font_size
                )

                self.main_window.blit(
                    instr_surface[0],
                    instr_surface[1].move(title_pos[0] + window_width * 0.2, title_pos[1]+text_font_size*1.25)
                )

                text_instr = f"PRESS WHITE BUTTON TO BEGIN THE TRAINING."
                instr_surface = self.font_instr.render(
                    text=text_instr,
                    fgcolor=LIGHT_GRAY,
                    size=instr_font_size
                )

                self.main_window.blit(
                    instr_surface[0],
                    instr_surface[1].move(text_pos[0] + window_width * 0.22, instr_pos[1])
                )

                pygame.display.flip()

            # While loop routine
            pygame.display.update()
            self.clock.tick_busy_loop(FPS)  # For more accurate display timer


if __name__ == '__main__':
    training = TestInstructions()
    training.test_instructions_run('keyboard', '16543')
