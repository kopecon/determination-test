import pygame
from pygame import VIDEORESIZE
import time

# -----------------------------------------------------------------------------------------  Import Custom Program Code:
from Tests import question_set
from Tests.test_environment import TestEnvironment


# ----------------------------------------------------------------------------------------------------------  Functions:
class Training(TestEnvironment):
    # Method that starts the test
    def run(self, phase="Instructions"):
        test_form = "Training"

        # Test title
        title = f"DETERMINATION TEST - {test_form.upper()}"
        pygame.display.set_caption(f"DT Test Form: {test_form}")

        # Declare test variables
        epoch_time = 0
        previous_stimulus_time_ms = 0
        stimulus_delay_time = 1040 * 2  # [ms] fixed stimulus time
        answered = False
        correct_answer = 0
        incorrect_answer = 0
        late_answer = 0
        missed_answer = 0
        tone_played = False
        stimulus_index = 0
        fullscreen = True  # Open test in fullscreen mode - fullscreen = True

        # Start circle at random position
        circle_position = self.random_circle_position()

        # Get the hardware configuration of the input device
        input_device_config = self.search_for_input_device()  # Hardware parameters
        panel_detected = input_device_config[0]  # Was control panel successfully detected?
        buttons = input_device_config[1]  # Hardware configuration of buttons or None if panel was not detected

        self.main_window.fill(self.GRAY)

        # Main while loop
        while True:
            # Use GPIO Button class only if the panel is detected
            self.scan_for_pressed_buttons(buttons, panel_detected)

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
                        self.main_window = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

                # Enter Fullscreen when pressing "f" on the keyboard
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

                # Scan for input (button/key)
                if event.type == pygame.KEYDOWN and not event.key == pygame.K_f:
                    # Start test by pressing any button/key
                    if phase == "Instructions":
                        phase = "Test"
                        self.main_window.fill(self.GRAY)
                        pygame.display.flip()
                        time.sleep(stimulus_delay_time / 1000)
                        # Clear Event Queue to prevent from reacting before stimulus shown
                        pygame.event.clear()
                        # Get epoch time
                        epoch_time = time.time_ns()

                    # Catch reaction
                    elif phase == "Test":

                        self.main_window.fill(self.GRAY)
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
                        time.sleep(self.debounce_time)

                    # Return to the menu by pressing any button/key if in the "Exit screen"

                    elif phase == "Exit Failure":
                        if event.key == pygame.K_g:
                            return "Success"
                        if event.key == pygame.K_r:
                            return "Failure"

            # Display START message
            if phase == "Instructions":

                text_title = title
                title_surface = self.title.render(
                    text=text_title,
                    fgcolor=self.LIGHT_GRAY,
                    size=self.title.size
                )
                self.main_window.blit(title_surface[0], title_surface[1].move(self.title_pos))

                text_text = "Following exercise is not being measured."
                text_surface = self.text.render(
                    text=text_text,
                    fgcolor=self.LIGHT_GRAY,
                    size=self.text.size
                )
                self.main_window.blit(
                    text_surface[0],
                    text_surface[1].move(self.text_pos[0], self.text_pos[1] + self.text.size * 1.25)
                )

                text_text = "Only one stimulus is being presented at a time."
                text_surface = self.text.render(
                    text=text_text,
                    fgcolor=self.LIGHT_GRAY,
                    size=self.text.size
                )
                self.main_window.blit(
                    text_surface[0],
                    text_surface[1].move(self.text_pos[0], self.text_pos[1] + self.text.size * 2.5)
                )

                text_text = "Try answering correctly."
                text_surface = self.text.render(
                    text=text_text,
                    fgcolor=self.LIGHT_GRAY,
                    size=self.text.size
                )
                self.main_window.blit(
                    text_surface[0],
                    text_surface[1].move(self.text_pos[0], self.text_pos[1] + self.text.size * 3.75)
                )

                text_text = "Tempo of the task assignment is fixed."
                text_surface = self.text.render(
                    text=text_text,
                    fgcolor=self.LIGHT_GRAY,
                    size=self.text.size
                )
                self.main_window.blit(
                    text_surface[0],
                    text_surface[1].move(self.text_pos[0], self.text_pos[1] + self.text.size * 5)
                )

                text_text_5 = f'''Training duration: {
                len(question_set.training_question_set) * stimulus_delay_time / 60 / 1000
                } min'''
                middle_text_text_5_surface = self.text.render(
                    text=text_text_5,
                    fgcolor=self.LIGHT_GRAY,
                    size=self.text.size
                )
                self.main_window.blit(
                    middle_text_text_5_surface[0],
                    middle_text_text_5_surface[1].move(self.text_pos[0], self.text_pos[1] + self.text.size * 8.75)
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

            # Start the test
            elif phase == "Test":
                # Set "time zero" when running the test
                current_script_time_ms = (time.time_ns() - epoch_time) / 1000000

                # Display stimulus
                if not answered:
                    self.main_window.fill(self.GRAY)
                    question_set_index = question_set.training_question_set[stimulus_index]
                    if not tone_played:  # Prevent looping of the sound
                        self.stimulus(question_set_index, circle_position)
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
                    if stimulus_index < len(question_set.training_question_set) - 1 - 22:
                        stimulus_index += 1
                        # Change circle position
                        circle_position = self.random_circle_position()
                    else:
                        self.main_window.fill(self.GRAY)
                        pygame.display.flip()

                        text_text = "Loading..."
                        title_surface = self.text.render(
                            text=text_text,
                            fgcolor=self.LIGHT_GRAY,
                            size=self.text.size
                        )
                        self.main_window.blit(
                            title_surface[0], title_surface[1].move(self.window_width * 0.44, self.text_pos[1] * 1.5))
                        pygame.display.flip()

                        time.sleep(2)

                        self.main_window.fill(self.GRAY)
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
                title_surface = self.title.render(
                    text=text_title,
                    fgcolor=self.LIGHT_GRAY,
                    size=self.title.size
                )
                self.main_window.blit(title_surface[0], title_surface[1].move(self.title_pos))

                text_text = "The training is finished."
                text_surface = self.text.render(
                    text=text_text,
                    fgcolor=self.LIGHT_GRAY,
                    size=self.text.size
                )
                self.main_window.blit(text_surface[0], text_surface[1].move(self.text_pos))

                text_text = f"Result:   Failure"
                text_surface = self.text.render(
                    text=text_text,
                    fgcolor=self.LIGHT_GRAY,
                    size=self.text.size
                )
                self.main_window.blit(
                    text_surface[0],
                    text_surface[1].move(self.text_pos[0], self.text_pos[1] + self.text.size * 2.5)
                )

                text_instr = "GREEN BUTTON: TEST"
                instr_surface = self.instr.render(
                    text=text_instr,
                    fgcolor=self.GREEN,
                    size=self.instr.size
                )
                self.main_window.blit(
                    instr_surface[0],
                    instr_surface[1].move(self.text_pos[0] + self.window_width * 0.58, self.instr_pos[1])
                )
                pygame.display.flip()

                text_instr = "RED BUTTON:   INSTRUCTIONS"
                instr_surface = self.instr.render(
                    text=text_instr,
                    fgcolor=self.RED,
                    size=self.instr.size
                )
                self.main_window.blit(
                    instr_surface[0],
                    instr_surface[1].move(self.text_pos[0], self.instr_pos[1])
                )
                pygame.display.flip()

            # While loop routine
            pygame.display.update()
            self.clock.tick_busy_loop(self.FPS)  # For more accurate display timer


if __name__ == '__main__':
    Training().run()
