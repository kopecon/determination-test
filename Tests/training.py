import pygame
from pygame import mixer, VIDEORESIZE, freetype
from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import Button
import random
import time
import os

# -----------------------------------------------------------------------------------------   Import Custom Program Code

from Tests import question_set

# ----------------------------------------------------------------------------------------------   Adjustable parameters


# Display parameters
FPS = 2000  # Frame rate celling

# Test parameters
test_duration = 240000  # Test duration in ms (4 min by default)
volume = 0.2  # Volume of the sound stimulus - Values from 0 to 1 (1 = Max volume) [%]
stimulus_delay_time = 1040*2  # [ms] fixed stimulus time

# Stimulus parameters
circle_size = 100  # Radius of the color circle stimulus [pixel]
pedal_width = 150  # Width of the pedal symbol [pixel]
pedal_height = 250  # Height of the pedal symbol [pixel]

# Switch debounce time [s] - empirically measured time (countermeasure to left pedal "Switch Bounce")
debounce_time = 0.2  # Could be around 190 ms

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

# Directory to search for dependencies
project_dir = os.path.join(os.getcwd(), os.pardir)
tests_style_dir = f'{project_dir}/Tests/Style'


# ----------------------------------------------------------------------------------------------------------   Functions
# Simulate keyboard press with GPIO Button
def pressing_button(unicode, represented_key):
    button_event = pygame.event.Event(
        pygame.KEYDOWN,
        unicode=unicode,
        key=represented_key,
        mod=pygame.KMOD_NONE
    )
    pygame.event.post(button_event)


# Define Stimulus Type
def stimulus(main_window, question_set_index, circle_position):

    # Set up sound bank
    high_tone = mixer.Sound(f'{tests_style_dir}/Sounds/High.wav')
    high_tone.set_volume(volume)
    low_tone = mixer.Sound(f'{tests_style_dir}/Sounds/Low.wav')
    low_tone.set_volume(volume)

    # Color Circles
    if question_set_index == "red":
        pygame.draw.circle(main_window, RED, circle_position, circle_size)

    elif question_set_index == "blue":
        pygame.draw.circle(main_window, BLUE, circle_position, circle_size)

    elif question_set_index == "green":
        pygame.draw.circle(main_window, GREEN, circle_position, circle_size)

    elif question_set_index == "yellow":
        pygame.draw.circle(main_window, YELLOW, circle_position, circle_size)

    elif question_set_index == "white":
        pygame.draw.circle(main_window, WHITE, circle_position, circle_size)

    # Pedals
    elif question_set_index == "left_pedal":
        pygame.draw.rect(main_window,
                         (253, 253, 253),
                         (50, int(main_window.get_height() - pedal_height - 50),
                          pedal_width,
                          pedal_height))

    elif question_set_index == "right_pedal":
        pygame.draw.rect(main_window,
                         (253, 253, 253),
                         (int(main_window.get_width() - pedal_width - 50),
                          int(main_window.get_height() - pedal_height - 50),
                          pedal_width,
                          pedal_height))

    # Sound
    elif question_set_index == "high_tone":
        high_tone.play(loops=0, maxtime=int(stimulus_delay_time), fade_ms=10)

    elif question_set_index == "low_tone":
        low_tone.play(loops=0, maxtime=int(stimulus_delay_time), fade_ms=10)


# Method that starts the test
def run(input_device=None, device_ip=None, phase="Instructions"):
    phase = phase                                                         # Choose in which phase you start the training

    # Test title
    title = "DETERMINATION TEST - TRAINING"

    # Text properties
    font_title = f'{tests_style_dir}/Fonts/Handgotn.ttf'
    title_font_size = 70
    font_text = f'{tests_style_dir}/Fonts/BebasNeue Book.ttf'
    text_font_size = 55
    font_instr = f'{tests_style_dir}/Fonts/BebasNeue Regular.ttf'
    instr_font_size = 60

    # Initialize Pygame
    pygame.init()

    # Get Monitor Info
    monitor_size = [pygame.display.Info().current_w, pygame.display.Info().current_h]
    window_width = monitor_size[0]
    window_height = monitor_size[1]

    # Set up the window
    main_window = pygame.display.set_mode((window_width, window_height), pygame.FULLSCREEN)
    pygame.display.set_caption("Training")

    main_window.fill(GRAY)

    # Declare buttons (if panel is found, the buttons are remapped as hardware buttons)
    white_button = None
    yellow_button = None
    green_button = None
    blue_button = None
    red_button = None
    up_button = None
    down_button = None
    left_pedal = None
    right_pedal = None

    # Declare test variables
    epoch_time = 0
    previous_stimulus_time_ms = 0
    answered = False
    correct_answer = 0
    incorrect_answer = 0
    late_answer = 0
    missed_answer = 0
    tone_played = False

    # Start circle at random position
    circle_position = [random.randint(0 + circle_size * 3, main_window.get_width() - circle_size * 3),
                       random.randint(0 + circle_size * 3, main_window.get_height() - circle_size * 3)]

    # Define clock
    clock = pygame.time.Clock()

    # Check for selected device
    if input_device == "Control panel":
        # Protect if panel IP address is not found
        try:
            # Create a connection to the Raspberry Pi remote GPIO
            factory = PiGPIOFactory(host=device_ip)

            # Create a connection to the Raspberry Pi remote GPIO (hardware configuration)
            white_button = Button(18, pin_factory=factory, pull_up=False)
            yellow_button = Button(14, pin_factory=factory, pull_up=False)
            green_button = Button(15, pin_factory=factory, pull_up=False)
            blue_button = Button(22, pin_factory=factory, pull_up=False)
            red_button = Button(27, pin_factory=factory, pull_up=False)
            up_button = Button(23, pin_factory=factory, pull_up=False)
            down_button = Button(17, pin_factory=factory, pull_up=False)
            left_pedal = Button(24, pin_factory=factory, pull_up=False)
            right_pedal = Button(25, pin_factory=factory, pull_up=False)
            panel_detected = True

        # Return to menu if panel is not found
        except OSError:
            panel_detected = False
            return panel_detected
    else:
        panel_detected = False

    # Start with first stimulus from the list
    stimulus_index = 0

    # Start in fullscreen
    fullscreen = True

    # Text properties
    font_title = pygame.freetype.Font(font_title, 70)
    title_pos = (100, window_height / 6 - title_font_size * 1.5)
    font_text = pygame.freetype.Font(font_text, 70)
    text_pos = (150, window_height / 3 - text_font_size * 1.5)
    font_instr = pygame.freetype.Font(font_instr, 70)
    instr_pos = (150, window_height / 1.05 - instr_font_size * 1.5)

    # Main while loop
    while True:
        # Use GPIO Button class only if the panel is detected
        if panel_detected:
            # Check for button pressing
            if white_button.is_pressed:
                pressing_button("w", pygame.K_w)
            if yellow_button.is_pressed:
                pressing_button("y", pygame.K_y)
            if green_button.is_pressed:
                pressing_button("g", pygame.K_g)
            if blue_button.is_pressed:
                pressing_button("b", pygame.K_b)
            if red_button.is_pressed:
                pressing_button("r", pygame.K_r)
            if up_button.is_pressed:
                pressing_button(None, pygame.K_UP)
            if down_button.is_pressed:
                pressing_button(None, pygame.K_DOWN)
            if left_pedal.is_pressed:
                pressing_button(None, pygame.K_LEFT)
            if right_pedal.is_pressed:
                pressing_button(None, pygame.K_RIGHT)

        # Event loop
        for event in pygame.event.get():

            # Closing the window by pressing X button on the window screen
            if event.type == pygame.QUIT:
                return "Interrupted"

            # Closing the window by pressing ESC
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "Interrupted"

            # Update screen size when manually resizing window
            if event.type == VIDEORESIZE:
                if not fullscreen:
                    main_window = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

            # Enter Fullscreen when pressing "f" on the keyboard
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_f:
                    fullscreen = not fullscreen
                    if fullscreen:
                        main_window = pygame.display.set_mode(monitor_size, pygame.FULLSCREEN)

                    else:
                        main_window = pygame.display.set_mode(
                            (int(main_window.get_width() - 500),
                             int(main_window.get_height()) - 500),
                            pygame.RESIZABLE)

            # Scan for input (button/key)
            if event.type == pygame.KEYDOWN and not event.key == pygame.K_f:
                # Start test by pressing any button/key
                if phase == "Instructions":
                    phase = "Test"
                    main_window.fill(GRAY)
                    pygame.display.flip()
                    time.sleep(stimulus_delay_time / 1000)
                    # Clear Event Queue to prevent from reacting before stimulus shown
                    pygame.event.clear()
                    # Get epoch time
                    epoch_time = time.time_ns()

                # Catch reaction
                elif phase == "Test":

                    main_window.fill(GRAY)
                    pygame.display.flip()

                    pygame.mixer.stop()

                    # Get response time
                    # Check for answer properties and insert them to answer table
                    # Correct Answer
                    if event.key == question_set.training_answer_set[stimulus_index] \
                            and not answered:
                        correct_answer += 1
                    # Incorrect Answer
                    elif not event.key == question_set.training_answer_set[stimulus_index] \
                            and not event.key == question_set.training_answer_set[stimulus_index - 1] \
                            and not answered:
                        incorrect_answer += 1
                    # Late Answer
                    elif not event.key == question_set.training_answer_set[stimulus_index] \
                            and event.key == question_set.training_answer_set[stimulus_index - 1] \
                            and not answered:
                        late_answer += 1

                    # Repeated Answer
                    elif answered:
                        incorrect_answer += 1
                        # Prevent over clogging of the event queue by spamming answers
                        pygame.event.clear()

                    answered = True

                    # Debounce GPIO input (It takes 200 ms for another input to be recognized)
                    time.sleep(debounce_time)

                # Return to the menu by pressing any button/key if in the "Exit screen"

                elif phase == "Exit Failure":
                    if event.key == pygame.K_g:
                        return "Success"
                    if event.key == pygame.K_r:
                        return "Failure"

        # Display START message
        if phase == "Instructions":

            text_title = title
            title_surface = font_title.render(
                text=text_title,
                fgcolor=LIGHT_GRAY,
                size=title_font_size
            )
            main_window.blit(title_surface[0], title_surface[1].move(title_pos))

            text_text = "Following exercise is not being measured."
            text_surface = font_text.render(
                text=text_text,
                fgcolor=LIGHT_GRAY,
                size=text_font_size
            )
            main_window.blit(
                text_surface[0],
                text_surface[1].move(text_pos[0], text_pos[1] + text_font_size * 1.25)
            )

            text_text = "Only one stimulus is being presented at a time."
            text_surface = font_text.render(
                text=text_text,
                fgcolor=LIGHT_GRAY,
                size=text_font_size
            )
            main_window.blit(
                text_surface[0],
                text_surface[1].move(text_pos[0], text_pos[1] + text_font_size * 2.5)
            )

            text_text = "Try answering correctly."
            text_surface = font_text.render(
                text=text_text,
                fgcolor=LIGHT_GRAY,
                size=text_font_size
            )
            main_window.blit(
                text_surface[0],
                text_surface[1].move(text_pos[0], text_pos[1] + text_font_size * 3.75)
            )

            text_text = "Tempo of the task assignment is fixed."
            text_surface = font_text.render(
                text=text_text,
                fgcolor=LIGHT_GRAY,
                size=text_font_size
            )
            main_window.blit(
                text_surface[0],
                text_surface[1].move(text_pos[0], text_pos[1] + text_font_size * 5)
            )

            text_text_5 = f'''Training duration: {
            len(question_set.training_question_set) * stimulus_delay_time / 60 / 1000
            } min'''
            middle_text_text_5_surface = font_text.render(
                text=text_text_5,
                fgcolor=LIGHT_GRAY,
                size=text_font_size
            )
            main_window.blit(
                middle_text_text_5_surface[0],
                middle_text_text_5_surface[1].move(text_pos[0], text_pos[1] + text_font_size * 8.75)
            )

            text_instr = "PRESS ANY BUTTON TO BEGIN"
            instr_surface = font_instr.render(
                text=text_instr,
                fgcolor=LIGHT_GRAY,
                size=instr_font_size
            )
            main_window.blit(
                instr_surface[0],
                instr_surface[1].move(text_pos[0] + window_width * 0.6, instr_pos[1])
            )

        # Start the test
        elif phase == "Test":
            # Set "time zero" when running the test
            current_script_time_ms = (time.time_ns() - epoch_time) / 1000000

            # Display stimulus
            if not answered:
                main_window.fill(GRAY)
                question_set_index = question_set.training_question_set[stimulus_index]
                if not tone_played:                                                       # Prevent looping of the sound
                    stimulus(main_window, question_set_index, circle_position)
                if question_set_index == "high_tone" or question_set_index == "low_tone":
                    tone_played = True
                else:
                    tone_played = False

                pygame.display.flip()

            # Get individual time per stimulus
            stimulus_time = current_script_time_ms - previous_stimulus_time_ms

            # End of current stimulus
            if stimulus_time >= stimulus_delay_time:
                # Check for missed answers
                if not answered:
                    missed_answer += 1

                # Clear Event Queue to prevent from reacting before stimulus shown
                pygame.event.clear()

                # Next stimulus or finish test if ran out of stimulus
                if stimulus_index < len(question_set.training_question_set)-1-22:
                    stimulus_index += 1
                    # Change circle position
                    circle_position = [random.randint(0 + circle_size * 3, main_window.get_width() - circle_size * 3),
                                       random.randint(0 + circle_size * 3, main_window.get_height() - circle_size * 3)]
                else:
                    main_window.fill(GRAY)
                    pygame.display.flip()

                    text_text = "Loading..."
                    title_surface = font_text.render(
                        text=text_text,
                        fgcolor=LIGHT_GRAY,
                        size=title_font_size
                    )
                    main_window.blit(title_surface[0], title_surface[1].move(window_width * 0.44, text_pos[1] * 1.5))
                    pygame.display.flip()

                    time.sleep(2)

                    main_window.fill(GRAY)
                    pygame.display.flip()
                    if incorrect_answer >= 4 or missed_answer >= 4:
                        phase = "Exit Failure"
                    else:
                        return "Success"

                # Reset stimulus time
                previous_stimulus_time_ms = (time.time_ns() - epoch_time) / 1000000

                answered = False

        # Display EXIT Failure message
        elif phase == "Exit Failure":

            text_title = title
            title_surface = font_title.render(
                text=text_title,
                fgcolor=LIGHT_GRAY,
                size=title_font_size
            )
            main_window.blit(title_surface[0], title_surface[1].move(title_pos))

            text_text = "The training is finished."
            text_surface = font_text.render(
                text=text_text,
                fgcolor=LIGHT_GRAY,
                size=text_font_size
            )
            main_window.blit(text_surface[0], text_surface[1].move(text_pos))

            text_text = f"Result:   Failure"
            text_surface = font_text.render(
                text=text_text,
                fgcolor=LIGHT_GRAY,
                size=text_font_size
            )
            main_window.blit(
                text_surface[0],
                text_surface[1].move(text_pos[0], text_pos[1] + text_font_size * 2.5)
            )

            text_instr = "GREEN BUTTON: TEST"
            instr_surface = font_instr.render(
                text=text_instr,
                fgcolor=GREEN,
                size=instr_font_size
            )
            main_window.blit(
                instr_surface[0],
                instr_surface[1].move(text_pos[0] + window_width * 0.58, instr_pos[1])
            )
            pygame.display.flip()

            text_instr = "RED BUTTON:   INSTRUCTIONS"
            instr_surface = font_instr.render(
                text=text_instr,
                fgcolor=RED,
                size=instr_font_size
            )
            main_window.blit(
                instr_surface[0],
                instr_surface[1].move(text_pos[0], instr_pos[1])
            )
            pygame.display.flip()

        # While loop routine
        pygame.display.update()
        clock.tick_busy_loop(FPS)  # For more accurate display timer


if __name__ == '__main__':
    run()
