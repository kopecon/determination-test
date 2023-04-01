import pygame
from pygame import VIDEORESIZE
import time

# -----------------------------------------------------------------------------------------  Import Custom Program Code:
from Tests.test_environment import TestEnvironment
from Tests import training


# ----------------------------------------------------------------------------------------------------------  Functions:
class Instructions(TestEnvironment):
    # Define Stimulus Type
    def stimulus(self, question_set_index, circle_position, sound_duration=1500):
        up_arrow_scale_factor = (100, 100)
        up_arrow_surface = pygame.Surface((200, 200))
        up_arrow_surface.fill(self.GRAY)
        down_arrow_scale_factor = (100, 100)

        # Color Circles
        if question_set_index == "RED":
            pygame.draw.circle(self.main_window, self.RED, circle_position, self.circle_size)

        elif question_set_index == "BLUE":
            pygame.draw.circle(self.main_window, self.BLUE, circle_position, self.circle_size)

        elif question_set_index == "GREEN":
            pygame.draw.circle(self.main_window, self.GREEN, circle_position, self.circle_size)

        elif question_set_index == "YELLOW":
            pygame.draw.circle(self.main_window, self.YELLOW, circle_position, self.circle_size)

        elif question_set_index == "WHITE":
            pygame.draw.circle(self.main_window, self.WHITE, circle_position, self.circle_size)

        # Pedals
        elif question_set_index == "Left Pedal":
            pygame.draw.rect(self.main_window,
                             self.WHITE,
                             (50, int(self.main_window.get_height() - self.pedal_height - 50),
                              self.pedal_width,
                              self.pedal_height))

        elif question_set_index == "Right Pedal":
            pygame.draw.rect(self.main_window,
                             self.WHITE,
                             (int(self.main_window.get_width() - self.pedal_width - 50),
                              int(self.main_window.get_height() - self.pedal_height - 50),
                              self.pedal_width,
                              self.pedal_height))

        # Sound
        elif question_set_index == "High Tone":
            if pygame.mixer.get_busy():
                pygame.mixer.stop()
                pygame.time.wait(100)
            self.high_tone.play(loops=0, fade_ms=10)

        elif question_set_index == "Low Tone":
            if pygame.mixer.get_busy():
                pygame.mixer.stop()
                pygame.time.wait(100)
            self.low_tone.play(loops=0, fade_ms=10)

        elif question_set_index == "Up Arrow":
            pygame.draw.circle(up_arrow_surface, (self.GRAY[0] - 28, self.GRAY[1] - 28, self.GRAY[2] - 28),
                               (100, 100), 100)
            pygame.draw.polygon(up_arrow_surface, self.WHITE, ((90, 160), (90, 100), (70, 100), (100, 40), (130, 100),
                                                               (110, 100), (110, 160)))
            scaled_arrow = pygame.transform.smoothscale(up_arrow_surface, up_arrow_scale_factor)
            up_arrow_rect = scaled_arrow.get_rect(center=(
                self.main_window.get_width() / 2,
                self.main_window.get_height() / 2 - 100)
            )
            self.main_window.blit(scaled_arrow, up_arrow_rect)

        elif question_set_index == "Down Arrow":
            pygame.draw.circle(up_arrow_surface, (self.GRAY[0] - 28, self.GRAY[1] - 28, self.GRAY[2] - 28),
                               (100, 100), 100)
            pygame.draw.polygon(up_arrow_surface, self.WHITE, ((90, 160), (90, 100), (70, 100), (100, 40), (130, 100),
                                                               (110, 100), (110, 160)))
            scaled_arrow = pygame.transform.smoothscale(up_arrow_surface, down_arrow_scale_factor)
            down_arrow = pygame.transform.rotate(scaled_arrow, 180)
            down_arrow_rect = scaled_arrow.get_rect(center=(
                self.main_window.get_width() / 2,
                self.main_window.get_height() / 2 + 100)
            )
            self.main_window.blit(down_arrow, down_arrow_rect)

    def run(self, phase="Color stimuli instructions"):
        test_form = "INSTRUCTIONS"

        # Test title
        title = f"DETERMINATION TEST - {test_form.upper()}"
        pygame.display.set_caption(f"DT Test Form: {test_form}")

        self.main_window.fill(self.GRAY)

        # Declare test specific variables
        stimulus_index = 0
        fullscreen = True
        instructions_color_stimulus_answer_set = [pygame.K_w, pygame.K_y, pygame.K_b, pygame.K_g, pygame.K_r]
        instructions_pedal_question_set = ["Left Pedal", "Right Pedal", "Left Pedal", "Right Pedal"]
        instructions_pedal_answer_set = [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_LEFT, pygame.K_RIGHT]
        instructions_color_stimulus_question_set = ["WHITE", "YELLOW", "BLUE", "GREEN", "RED"]
        circle_position = [self.main_window.get_width() / 2, self.main_window.get_height() / 2]

        # Get the hardware configuration of the input device
        input_device_config = self.search_for_input_device()  # Hardware parameters
        panel_detected = input_device_config[0]  # Was control panel successfully detected?
        buttons = input_device_config[1]  # Hardware configuration of buttons or None if panel was not detected

        self.main_window.fill(self.GRAY)

        # Main While loop
        while True:
            # Use GPIO Button class only if the panel is detected
            self.scan_for_pressed_buttons(buttons, panel_detected)

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
                        self.main_window = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

                # Enter Fullscreen when pressing "f"
                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_f:
                        fullscreen = not fullscreen
                        if fullscreen:
                            self.main_window = pygame.display.set_mode(self.monitor_size, pygame.FULLSCREEN)

                        else:
                            self.main_window = pygame.display.set_mode(
                                (int(self.main_window.get_width() - 500),
                                 int(self.main_window.get_height()) - 500),
                                pygame.RESIZABLE)

                # Catch reaction
                if event.type == pygame.KEYDOWN and not event.key == pygame.K_f:
                    # First Checkpoint
                    if phase == "Color stimuli instructions":
                        stimulus_index = 0
                        phase = "Color stimuli testing"
                        self.main_window.fill(self.GRAY)
                        pygame.display.flip()
                        time.sleep(0.5)

                    # Color Stimulus Instructions
                    elif phase == "Color stimuli testing" \
                            and event.key == instructions_color_stimulus_answer_set[stimulus_index]:
                        if stimulus_index < len(instructions_color_stimulus_question_set) - 1:
                            stimulus_index += 1
                            self.main_window.fill(self.GRAY)
                            pygame.display.flip()
                            time.sleep(0.25)
                        else:
                            phase = "Pedal stimuli instructions"
                            stimulus_index = 0
                            self.main_window.fill(self.GRAY)
                            pygame.display.flip()
                            time.sleep(0.25)

                    # Second Checkpoint
                    elif phase == "Pedal stimuli instructions":
                        phase = "Pedal stimuli testing"
                        self.main_window.fill(self.GRAY)
                        pygame.display.flip()
                        time.sleep(0.5)

                    # Pedals Instructions
                    elif phase == "Pedal stimuli testing" \
                            and event.key == instructions_pedal_answer_set[stimulus_index]:
                        if stimulus_index < len(instructions_pedal_question_set) - 1:
                            stimulus_index += 1
                            self.main_window.fill(self.GRAY)
                            pygame.display.flip()
                            time.sleep(0.25)
                        else:
                            stimulus_index = 0
                            phase = "Sound stimuli instructions"
                            self.main_window.fill(self.GRAY)
                            pygame.display.flip()
                            time.sleep(0.25)

                    # Third Checkpoint
                    elif phase == "Sound stimuli instructions":
                        stimulus_index = 0
                        phase = "Sound stimuli testing"
                        self.main_window.fill(self.GRAY)
                        pygame.display.flip()
                        time.sleep(0.5)

                    # Tone Instructions
                    elif phase == "Sound stimuli testing":
                        if event.key == pygame.K_UP:
                            self.stimulus("High Tone", circle_position)
                        elif event.key == pygame.K_DOWN:
                            self.stimulus("Low Tone", circle_position)
                        elif event.key == pygame.K_w:
                            stimulus_index = 0
                            result = training.run(self.device.input_device, self.device.device_ip)
                            if result == "Success":
                                return "Success"
                            else:
                                phase = "Color stimuli instructions"

            # First Checkpoint Message
            if phase == "Color stimuli instructions":
                self.main_window.fill(self.GRAY)
                text_title = title
                title_surface = self.title.render(
                    text=text_title,
                    fgcolor=self.LIGHT_GRAY,
                    size=self.title.size
                )
                self.main_window.blit(title_surface[0], title_surface[1].move(self.title_pos))

                text_instr = "COLOR STIMULI"
                text_surface = self.instr.render(
                    text=text_instr,
                    fgcolor=self.LIGHT_GRAY,
                    size=self.text.size
                )
                self.main_window.blit(text_surface[0], text_surface[1].move(self.text_pos))

                text_text = "Following exercises are not being measured."
                text_surface = self.text.render(
                    text=text_text,
                    fgcolor=self.LIGHT_GRAY,
                    size=self.text.size
                )
                self.main_window.blit(
                    text_surface[0],
                    text_surface[1].move(self.text_pos[0], self.text_pos[1] + self.text.size * 2.5)
                )

                text_text = "Only one stimulus is being presented at a time."
                text_surface = self.text.render(
                    text=text_text,
                    fgcolor=self.LIGHT_GRAY,
                    size=self.text.size
                )
                self.main_window.blit(
                    text_surface[0],
                    text_surface[1].move(self.text_pos[0], self.text_pos[1] + self.text.size * 3.75)
                )

                text_text = "Press the button with the same color as the stimuli shown on the screen."
                text_surface = self.text.render(
                    text=text_text,
                    fgcolor=self.LIGHT_GRAY,
                    size=self.text.size
                )
                self.main_window.blit(
                    text_surface[0],
                    text_surface[1].move(self.text_pos[0], self.text_pos[1] + self.text.size * 5)
                )

                text_instr = "PRESS ANY BUTTON TO BEGIN"
                instr_surface = self.instr.render(
                    text=text_instr,
                    fgcolor=self.LIGHT_GRAY,
                    size=self.instr.size
                )
                self.main_window.blit(
                    instr_surface[0],
                    instr_surface[1].move(self.text_pos[0] + self.window_width * 0.6, self.instr_pos[1])
                )

            # Display Color Stimulus instructions
            elif phase == "Color stimuli testing":
                if stimulus_index <= len(instructions_color_stimulus_question_set):
                    color_stimulus_question_set_index = instructions_color_stimulus_question_set[
                        stimulus_index]
                else:
                    color_stimulus_question_set_index = 0

                self.main_window.fill(self.GRAY)
                self.stimulus(color_stimulus_question_set_index, circle_position)

            # Second Checkpoint Message
            elif phase == "Pedal stimuli instructions":

                self.main_window.fill(self.GRAY)
                text_instr = "PEDALS"
                text_surface = self.instr.render(
                    text=text_instr,
                    fgcolor=self.LIGHT_GRAY,
                    size=self.text.size
                )
                self.main_window.blit(text_surface[0], text_surface[1].move(self.text_pos))

                text_text = "Following exercises are not being measured."
                text_surface = self.text.render(
                    text=text_text,
                    fgcolor=self.LIGHT_GRAY,
                    size=self.text.size
                )
                self.main_window.blit(
                    text_surface[0],
                    text_surface[1].move(self.text_pos[0], self.text_pos[1] + self.text.size * 2.5)
                )

                text_text = "Only one stimulus is being presented at a time."
                text_surface = self.text.render(
                    text=text_text,
                    fgcolor=self.LIGHT_GRAY,
                    size=self.text.size
                )
                self.main_window.blit(
                    text_surface[0],
                    text_surface[1].move(self.text_pos[0], self.text_pos[1] + self.text.size * 3.75)
                )

                text_text = "Press the pedal with the same position as the stimuli shown on the screen."
                text_surface = self.text.render(
                    text=text_text,
                    fgcolor=self.LIGHT_GRAY,
                    size=self.text.size
                )
                self.main_window.blit(
                    text_surface[0],
                    text_surface[1].move(self.text_pos[0], self.text_pos[1] + self.text.size * 5)
                )

                text_instr = "PRESS ANY BUTTON TO BEGIN"
                instr_surface = self.instr.render(
                    text=text_instr,
                    fgcolor=self.LIGHT_GRAY,
                    size=self.instr.size
                )
                self.main_window.blit(
                    instr_surface[0],
                    instr_surface[1].move(self.text_pos[0] + self.window_width * 0.6, self.instr_pos[1])
                )

            # Display Pedal instructions
            elif phase == "Pedal stimuli testing":
                if stimulus_index <= len(instructions_pedal_question_set):
                    pedal_question_set_index = instructions_pedal_question_set[stimulus_index]
                else:
                    pedal_question_set_index = 0
                self.main_window.fill(self.GRAY)
                self.stimulus(pedal_question_set_index, circle_position)
                pygame.display.flip()

            # Third Checkpoint Message
            elif phase == "Sound stimuli instructions":

                self.main_window.fill(self.GRAY)
                text_instr = "ACOUSTIC STIMULI"
                text_surface = self.instr.render(
                    text=text_instr,
                    fgcolor=self.LIGHT_GRAY,
                    size=self.text.size
                )
                self.main_window.blit(text_surface[0], text_surface[1].move(self.text_pos))

                text_text = "Following exercises are not being measured."
                text_surface = self.text.render(
                    text=text_text,
                    fgcolor=self.LIGHT_GRAY,
                    size=self.text.size
                )
                self.main_window.blit(
                    text_surface[0],
                    text_surface[1].move(self.text_pos[0], self.text_pos[1] + self.text.size * 2.5)
                )

                text_text = "Press the buttons to hear the sound they represent."
                text_surface = self.text.render(
                    text=text_text,
                    fgcolor=self.LIGHT_GRAY,
                    size=self.text.size
                )
                self.main_window.blit(
                    text_surface[0],
                    text_surface[1].move(self.text_pos[0], self.text_pos[1] + self.text.size * 3.75)
                )

                text_instr = "PRESS ANY BUTTON TO BEGIN"
                instr_surface = self.instr.render(
                    text=text_instr,
                    fgcolor=self.LIGHT_GRAY,
                    size=self.instr.size
                )
                self.main_window.blit(
                    instr_surface[0],
                    instr_surface[1].move(self.text_pos[0] + self.window_width * 0.6, self.instr_pos[1])
                )

            # Present Tone instructions
            elif phase == "Sound stimuli testing":

                self.main_window.fill(self.GRAY)
                self.stimulus("Up Arrow", circle_position)
                self.stimulus("Down Arrow", circle_position)

                text_instr = "PRESS UP ARROW BUTTON TO HEAR THE HIGH TONE."
                instr_surface = self.text.render(
                    text=text_instr,
                    fgcolor=self.LIGHT_GRAY,
                    size=self.instr.size
                )

                self.main_window.blit(
                    instr_surface[0],
                    instr_surface[1].move(self.title_pos[0] + self.window_width * 0.22, self.title_pos[1])
                )

                text_instr = "PRESS DOWN ARROW BUTTON TO HEAR THE LOW TONE."
                instr_surface = self.text.render(
                    text=text_instr,
                    fgcolor=self.LIGHT_GRAY,
                    size=self.instr.size
                )

                self.main_window.blit(
                    instr_surface[0],
                    instr_surface[1].move(
                        self.title_pos[0] + self.window_width * 0.2, self.title_pos[1] + self.text.size * 1.25)
                )

                text_instr = "PRESS WHITE BUTTON TO BEGIN THE TRAINING."
                instr_surface = self.instr.render(
                    text=text_instr,
                    fgcolor=self.LIGHT_GRAY,
                    size=self.instr.size
                )

                self.main_window.blit(
                    instr_surface[0],
                    instr_surface[1].move(self.text_pos[0] + self.window_width * 0.22, self.instr_pos[1])
                )

                pygame.display.flip()

            # While loop routine
            pygame.display.update()
            self.clock.tick_busy_loop(self.FPS)  # For more accurate display timer


if __name__ == '__main__':
    Instructions().run()
