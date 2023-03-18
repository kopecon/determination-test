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
def stimulus(main_window, selected_question):
    circle_position = [main_window.get_width() / 2, main_window.get_height() / 2]
    up_arrow_scale_factor = (100, 100)
    up_arrow_surface = pygame.Surface((200, 200))
    up_arrow_surface.fill(GRAY)
    down_arrow_scale_factor = (100, 100)

    # Set up sound bank
    high_tone = mixer.Sound(f'{tests_style_dir}/Sounds/High.wav')
    high_tone.set_volume(volume)
    low_tone = mixer.Sound(f'{tests_style_dir}/Sounds/Low.wav')
    low_tone.set_volume(volume)

    # Color Circles
    if selected_question == "red":
        pygame.draw.circle(main_window, RED, circle_position, circle_size)

    elif selected_question == "blue":
        pygame.draw.circle(main_window, BLUE, circle_position, circle_size)

    elif selected_question == "green":
        pygame.draw.circle(main_window, GREEN, circle_position, circle_size)

    elif selected_question == "yellow":
        pygame.draw.circle(main_window, YELLOW, circle_position, circle_size)

    elif selected_question == "white":
        pygame.draw.circle(main_window, WHITE, circle_position, circle_size)

    # Pedals
    elif selected_question == "Left Pedal":
        pygame.draw.rect(main_window,
                         WHITE,
                         (50, int(main_window.get_height() - pedal_height - 50),
                          pedal_width,
                          pedal_height))

    elif selected_question == "Right Pedal":
        pygame.draw.rect(main_window,
                         WHITE,
                         (int(main_window.get_width() - pedal_width - 50),
                          int(main_window.get_height() - pedal_height - 50),
                          pedal_width,
                          pedal_height))

    # Sound
    elif selected_question == "High Tone":
        if pygame.mixer.get_busy():
            pygame.mixer.stop()
            pygame.time.wait(100)
        high_tone.play(loops=0, fade_ms=10)

    elif selected_question == "Low Tone":
        if pygame.mixer.get_busy():
            pygame.mixer.stop()
            pygame.time.wait(100)
        low_tone.play(loops=0, fade_ms=10)

    elif selected_question == "Up Arrow":
        pygame.draw.circle(up_arrow_surface, (GRAY[0] - 28, GRAY[1] - 28, GRAY[2] - 28), (100, 100), 100)
        pygame.draw.polygon(up_arrow_surface, WHITE, (
            (90, 160),
            (90, 100),
            (70, 100),
            (100, 40),
            (130, 100),
            (110, 100),
            (110, 160)
        ))
        scaled_arrow = pygame.transform.smoothscale(up_arrow_surface, up_arrow_scale_factor)
        up_arrow_rect = scaled_arrow.get_rect(center=(
            main_window.get_width()/2,
            main_window.get_height()/2 - 100)
        )
        main_window.blit(scaled_arrow, up_arrow_rect)

    elif selected_question == "Down Arrow":
        pygame.draw.circle(up_arrow_surface, (GRAY[0] - 28, GRAY[1] - 28, GRAY[2] - 28), (100, 100), 100)
        pygame.draw.polygon(up_arrow_surface, WHITE, (
            (90, 160),
            (90, 100),
            (70, 100),
            (100, 40),
            (130, 100),
            (110, 100),
            (110, 160)
        ))
        scaled_arrow = pygame.transform.smoothscale(up_arrow_surface, down_arrow_scale_factor)
        down_arrow = pygame.transform.rotate(scaled_arrow, 180)
        down_arrow_rect = scaled_arrow.get_rect(center=(
            main_window.get_width() / 2,
            main_window.get_height() / 2 + 100)
        )
        main_window.blit(down_arrow, down_arrow_rect)


def run(input_device=None, device_ip=None, phase="Color stimuli instructions"):
    phase = phase                                                         # Choose in which phase you start the training

    # Instructions title
    title = "DETERMINATION TEST - INSTRUCTIONS"

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
    pygame.display.set_caption("Instructions")

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

    # Define clock
    clock = pygame.time.Clock()

    # Question and answers
    instructions_color_stimulus_answer_set = [
        pygame.K_w,
        pygame.K_y,
        pygame.K_b,
        pygame.K_g,
        pygame.K_r
    ]

    instructions_pedal_question_set = [
        "Left Pedal",
        "Right Pedal",
        "Left Pedal",
        "Right Pedal",
    ]

    instructions_pedal_answer_set = [
        pygame.K_LEFT,
        pygame.K_RIGHT,
        pygame.K_LEFT,
        pygame.K_RIGHT,
    ]

    instructions_color_stimulus_question_set = [
        "white",
        "yellow",
        "blue",
        "green",
        "red"
    ]

    # Check for selected device
    if input_device == "Control panel":
        try:
            # Create a connection to the Raspberry Pi remote GPIO (hardware configuration)
            factory = PiGPIOFactory(host=device_ip)
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
        except OSError:
            panel_detected = False
    else:
        panel_detected = False

    # Start at stimulus_index 0
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

    # Main While loop
    while True:
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

        for event in pygame.event.get():
            # Closing the window by pressing X button on the window screen
            if event.type == pygame.QUIT:
                pygame.quit()
                return True

            # Closing the window by pressing ESC
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return True

            # Update screen size when manually resizing window
            if event.type == VIDEORESIZE:
                if not fullscreen:
                    main_window = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

            # Enter Fullscreen when pressing "f"
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

            # Catch reaction
            if event.type == pygame.KEYDOWN and not event.key == pygame.K_f:
                # First Checkpoint
                if phase == "Color stimuli instructions":
                    stimulus_index = 0
                    phase = "Color stimuli testing"
                    main_window.fill(GRAY)
                    pygame.display.flip()
                    time.sleep(0.5)

                # Color Stimulus Instructions
                elif phase == "Color stimuli testing" \
                        and event.key == instructions_color_stimulus_answer_set[stimulus_index]:
                    if stimulus_index < len(instructions_color_stimulus_question_set) - 1:
                        stimulus_index += 1
                        main_window.fill(GRAY)
                        pygame.display.flip()
                        time.sleep(0.25)
                    else:
                        phase = "Pedal stimuli instructions"
                        stimulus_index = 0
                        main_window.fill(GRAY)
                        pygame.display.flip()
                        time.sleep(0.25)

                # Second Checkpoint
                elif phase == "Pedal stimuli instructions":
                    phase = "Pedal stimuli testing"
                    main_window.fill(GRAY)
                    pygame.display.flip()
                    time.sleep(0.5)

                # Pedals Instructions
                elif phase == "Pedal stimuli testing" \
                        and event.key == instructions_pedal_answer_set[stimulus_index]:
                    if stimulus_index < len(instructions_pedal_question_set) - 1:
                        stimulus_index += 1
                        main_window.fill(GRAY)
                        pygame.display.flip()
                        time.sleep(0.25)
                    else:
                        stimulus_index = 0
                        phase = "Sound stimuli instructions"
                        main_window.fill(GRAY)
                        pygame.display.flip()
                        time.sleep(0.25)

                # Third Checkpoint
                elif phase == "Sound stimuli instructions":
                    stimulus_index = 0
                    phase = "Sound stimuli testing"
                    main_window.fill(GRAY)
                    pygame.display.flip()
                    time.sleep(0.5)

                # Tone Instructions
                elif phase == "Sound stimuli testing":
                    if event.key == pygame.K_UP:
                        stimulus(main_window, "High Tone")
                    elif event.key == pygame.K_DOWN:
                        stimulus(main_window, "Low Tone")
                    elif event.key == pygame.K_w:
                        stimulus_index = 0
                        result = training.run(input_device, device_ip)
                        if result == "Success":
                            return "Success"
                        else:
                            phase = "Color stimuli instructions"

        # First Checkpoint Message
        if phase == "Color stimuli instructions":
            main_window.fill(GRAY)
            text_title = title
            title_surface = font_title.render(
                text=text_title,
                fgcolor=LIGHT_GRAY,
                size=title_font_size
            )
            main_window.blit(title_surface[0], title_surface[1].move(title_pos))

            text_instr = f"COLOR STIMULI"
            text_surface = font_instr.render(
                text=text_instr,
                fgcolor=LIGHT_GRAY,
                size=text_font_size
            )
            main_window.blit(text_surface[0], text_surface[1].move(text_pos))

            text_text = "Following exercises are not being measured."
            text_surface = font_text.render(
                text=text_text,
                fgcolor=LIGHT_GRAY,
                size=text_font_size
            )
            main_window.blit(
                text_surface[0],
                text_surface[1].move(text_pos[0], text_pos[1] + text_font_size * 2.5)
            )

            text_text = "Only one stimulus is being presented at a time."
            text_surface = font_text.render(
                text=text_text,
                fgcolor=LIGHT_GRAY,
                size=text_font_size
            )
            main_window.blit(
                text_surface[0],
                text_surface[1].move(text_pos[0], text_pos[1] + text_font_size * 3.75)
            )

            text_text = "Press the button with the same color as the stimuli shown on the screen."
            text_surface = font_text.render(
                text=text_text,
                fgcolor=LIGHT_GRAY,
                size=text_font_size
            )
            main_window.blit(
                text_surface[0],
                text_surface[1].move(text_pos[0], text_pos[1] + text_font_size * 5)
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

        # Display Color Stimulus instructions
        elif phase == "Color stimuli testing":
            if stimulus_index <= len(instructions_color_stimulus_question_set):
                color_stimulus_question_set_index = instructions_color_stimulus_question_set[
                    stimulus_index]
            else:
                color_stimulus_question_set_index = 0

            main_window.fill(GRAY)
            stimulus(main_window, color_stimulus_question_set_index)

        # Second Checkpoint Message
        elif phase == "Pedal stimuli instructions":

            main_window.fill(GRAY)
            text_instr = f"PEDALS"
            text_surface = font_instr.render(
                text=text_instr,
                fgcolor=LIGHT_GRAY,
                size=text_font_size
            )
            main_window.blit(text_surface[0], text_surface[1].move(text_pos))

            text_text = "Following exercises are not being measured."
            text_surface = font_text.render(
                text=text_text,
                fgcolor=LIGHT_GRAY,
                size=text_font_size
            )
            main_window.blit(
                text_surface[0],
                text_surface[1].move(text_pos[0], text_pos[1] + text_font_size * 2.5)
            )

            text_text = "Only one stimulus is being presented at a time."
            text_surface = font_text.render(
                text=text_text,
                fgcolor=LIGHT_GRAY,
                size=text_font_size
            )
            main_window.blit(
                text_surface[0],
                text_surface[1].move(text_pos[0], text_pos[1] + text_font_size * 3.75)
            )

            text_text = "Press the pedal with the same position as the stimuli shown on the screen."
            text_surface = font_text.render(
                text=text_text,
                fgcolor=LIGHT_GRAY,
                size=text_font_size
            )
            main_window.blit(
                text_surface[0],
                text_surface[1].move(text_pos[0], text_pos[1] + text_font_size * 5)
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

        # Display Pedal instructions
        elif phase == "Pedal stimuli testing":
            if stimulus_index <= len(instructions_pedal_question_set):
                pedal_question_set_index = instructions_pedal_question_set[stimulus_index]
            else:
                pedal_question_set_index = 0
            main_window.fill(GRAY)
            stimulus(main_window, pedal_question_set_index)
            pygame.display.flip()

        # Third Checkpoint Message
        elif phase == "Sound stimuli instructions":

            main_window.fill(GRAY)
            text_instr = f"ACOUSTIC STIMULI"
            text_surface = font_instr.render(
                text=text_instr,
                fgcolor=LIGHT_GRAY,
                size=text_font_size
            )
            main_window.blit(text_surface[0], text_surface[1].move(text_pos))

            text_text = "Following exercises are not being measured."
            text_surface = font_text.render(
                text=text_text,
                fgcolor=LIGHT_GRAY,
                size=text_font_size
            )
            main_window.blit(
                text_surface[0],
                text_surface[1].move(text_pos[0], text_pos[1] + text_font_size * 2.5)
            )

            text_text = "Press the buttons to hear the sound they represent."
            text_surface = font_text.render(
                text=text_text,
                fgcolor=LIGHT_GRAY,
                size=text_font_size
            )
            main_window.blit(
                text_surface[0],
                text_surface[1].move(text_pos[0], text_pos[1] + text_font_size * 3.75)
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

        # Present Tone instructions
        elif phase == "Sound stimuli testing":

            main_window.fill(GRAY)
            stimulus(main_window, "Up Arrow")
            stimulus(main_window, "Down Arrow")

            text_instr = f"PRESS UP ARROW BUTTON TO HEAR THE HIGH TONE."
            instr_surface = font_text.render(
                text=text_instr,
                fgcolor=LIGHT_GRAY,
                size=instr_font_size
            )

            main_window.blit(
                instr_surface[0],
                instr_surface[1].move(title_pos[0]+window_width*0.22, title_pos[1])
            )

            text_instr = f"PRESS DOWN ARROW BUTTON TO HEAR THE LOW TONE."
            instr_surface = font_text.render(
                text=text_instr,
                fgcolor=LIGHT_GRAY,
                size=instr_font_size
            )

            main_window.blit(
                instr_surface[0],
                instr_surface[1].move(title_pos[0] + window_width * 0.2, title_pos[1]+text_font_size*1.25)
            )

            text_instr = f"PRESS WHITE BUTTON TO BEGIN THE TRAINING."
            instr_surface = font_instr.render(
                text=text_instr,
                fgcolor=LIGHT_GRAY,
                size=instr_font_size
            )

            main_window.blit(
                instr_surface[0],
                instr_surface[1].move(text_pos[0] + window_width * 0.22, instr_pos[1])
            )

            pygame.display.flip()

        # While loop routine
        pygame.display.update()
        clock.tick_busy_loop(FPS)  # For more accurate display timer


if __name__ == '__main__':
    run()
