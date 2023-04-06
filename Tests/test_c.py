import pygame
import time

# -----------------------------------------------------------------------------------------  Import Custom Program Code:

from Database import user_database
from Tests import question_set
from Tests.test_environment import TestEnvironment


# ----------------------------------------------------------------------------------------------------------  Functions:
class TestC(TestEnvironment):
    # Method that starts the test
    def run(self, phase="Instructions"):

        test_form = "C"

        # Test title
        title = f"DETERMINATION TEST - {test_form.upper()} FORM"
        pygame.display.set_caption(f"DT Test Form: {test_form}")

        # Declare test variables
        epoch_time = 0
        reset_respond_time_ms = 0
        stimulus_index = 0
        tone_played = False

        # Start circle at random position
        circle_position = self.random_circle_position()

        # Get the hardware configuration of the input device
        input_device_config = self.search_for_input_device()  # Hardware parameters
        panel_detected = input_device_config[0]  # Was control panel successfully detected?
        buttons = input_device_config[1]  # Hardware configuration of buttons or None if panel was not detected

        # Record answers for current user if the user is in the user database
        username = self.record_answers(test_form)[0]  # Get username of the user who is being tested
        score_id = self.record_answers(test_form)[1]  # Get the ID of the score for the current test

        self.main_window.fill(self.color_scheme['GRAY'])

        # Main while loop
        while True:
            # Use GPIO Button class only if the panel is detected
            self.scan_for_pressed_buttons(buttons, panel_detected)

            # Event loop
            for event in pygame.event.get():

                # Exit test environment if pressed "ESC" key or "close" button
                if self.exit(phase, event, score_id):
                    return

                # Scan for input (button/key)
                if event.type == pygame.KEYDOWN and not event.key == pygame.K_f:

                    # Prepare new random position
                    circle_position = self.random_circle_position()

                    # Start test by pressing any button/key
                    if phase == "Instructions":
                        phase = "Test"
                        self.main_window.fill(self.color_scheme['GRAY'])
                        pygame.display.flip()
                        time.sleep(2)
                        # Clear Event Queue to prevent from reacting before stimulus shown
                        pygame.event.clear()
                        # Get epoch time
                        epoch_time = time.time_ns()

                    # Catch reaction
                    elif phase == "Test":

                        self.main_window.fill(self.color_scheme['GRAY'])
                        pygame.display.flip()

                        pygame.mixer.pause()

                        # Get response time
                        press_time_ns = (time.time_ns() - epoch_time)
                        current_script_time_ms = press_time_ns / 1000000
                        response_time_ns = press_time_ns - reset_respond_time_ms * 1000000

                        # Reset respond time
                        previous_stimulus_time_ms = (time.time_ns() - epoch_time) / 1000000
                        reset_respond_time_ms = previous_stimulus_time_ms

                        # Check for answer properties and insert them to answer table
                        # Correct Answer
                        if event.key == question_set.answer_set[stimulus_index]:

                            # Insert correct answer in to answer table
                            user_database.insert_into_answer_table(
                                question_set.question_set[stimulus_index],
                                pygame.key.name(event.key),
                                "Correct",
                                current_script_time_ms / 1000,
                                response_time_ns / 1000000,
                                score_id
                            )

                        # Incorrect Answer
                        elif not event.key == question_set.answer_set[stimulus_index] \
                                and not event.key == question_set.answer_set[stimulus_index - 1]:

                            # Insert incorrect answer in to answer table
                            user_database.insert_into_answer_table(
                                question_set.question_set[stimulus_index],
                                pygame.key.name(event.key),
                                "Incorrect",
                                current_script_time_ms / 1000,
                                response_time_ns / 1000000,
                                score_id
                            )

                        # Next stimulus
                        if stimulus_index < len(question_set.question_set) - 1:
                            stimulus_index += 1

                        # Finish test after stimuli runs out
                        else:
                            self.main_window.fill(self.color_scheme['GRAY'])
                            pygame.display.flip()

                            time.sleep(1)

                            text_text = "Loading..."
                            title_surface = self.text.render(
                                text=text_text,
                                fgcolor=self.color_scheme['LIGHT_GRAY'],
                                size=self.text.size
                            )
                            self.main_window.blit(title_surface[0],
                                                  title_surface[1].move(
                                                      int(self.main_window.get_width()) * 0.44, self.text_pos[1] * 1.5))
                            pygame.display.flip()

                            time.sleep(2)

                            self.main_window.fill(self.color_scheme['GRAY'])
                            pygame.display.flip()

                            phase = "Exit"

                            self.main_window.fill(self.color_scheme['GRAY'])
                            pygame.display.flip()

                        # Debounce GPIO input (It takes 200 ms for another input to be recognized)
                        time.sleep(self.debounce_time)

                    # Return to the menu by pressing any button/key if in the "Exit screen"
                    elif phase == "Exit":
                        pygame.quit()
                        return

            # Display START message
            if phase == "Instructions":
                self.main_window.fill(self.color_scheme['GRAY'])

                text_title = title
                title_surface = self.title.render(
                    text=text_title,
                    fgcolor=self.color_scheme['LIGHT_GRAY'],
                    size=self.title.size
                )
                self.main_window.blit(title_surface[0], title_surface[1].move(self.title_pos))

                text_text = f"User:       {username}"
                text_surface = self.text.render(
                    text=text_text,
                    fgcolor=self.color_scheme['LIGHT_GRAY'],
                    size=self.text.size
                )
                self.main_window.blit(text_surface[0], text_surface[1].move(self.text_pos))

                text_text = "Following test is being measured."
                text_surface = self.text.render(
                    text=text_text,
                    fgcolor=self.color_scheme['LIGHT_GRAY'],
                    size=self.text.size
                )
                self.main_window.blit(
                    text_surface[0],
                    text_surface[1].move(self.text_pos[0], self.text_pos[1] + self.text.size * 2.5)
                )

                text_text = "Only one stimulus is being presented at a time."
                text_surface = self.text.render(
                    text=text_text,
                    fgcolor=self.color_scheme['LIGHT_GRAY'],
                    size=self.text.size
                )
                self.main_window.blit(
                    text_surface[0],
                    text_surface[1].move(self.text_pos[0], self.text_pos[1] + self.text.size * 3.75)
                )

                text_text = "React as fast as possible."
                text_surface = self.text.render(
                    text=text_text,
                    fgcolor=self.color_scheme['LIGHT_GRAY'],
                    size=self.text.size
                )
                self.main_window.blit(
                    text_surface[0],
                    text_surface[1].move(self.text_pos[0], self.text_pos[1] + self.text.size * 5)
                )

                text_text = "Next task is assigned after answering the previous one."
                text_surface = self.text.render(
                    text=text_text,
                    fgcolor=self.color_scheme['LIGHT_GRAY'],
                    size=self.text.size
                )
                self.main_window.blit(
                    text_surface[0],
                    text_surface[1].move(self.text_pos[0], self.text_pos[1] + self.text.size * 6.25)
                )

                text_text_5 = f"Test duration:  Undefined"
                middle_text_text_5_surface = self.text.render(
                    text=text_text_5,
                    fgcolor=self.color_scheme['LIGHT_GRAY'],
                    size=self.text.size
                )
                self.main_window.blit(
                    middle_text_text_5_surface[0],
                    middle_text_text_5_surface[1].move(self.text_pos[0], self.text_pos[1] + self.text.size * 8.75)
                )

                text_instr = "PRESS ANY BUTTON TO BEGIN"
                instr_surface = self.instr.render(
                    text=text_instr,
                    fgcolor=self.color_scheme['LIGHT_GRAY'],
                    size=self.instr.size
                )
                self.main_window.blit(
                    instr_surface[0],
                    instr_surface[1].move(self.text_pos[0] + int(self.main_window.get_width()) * 0.6, self.instr_pos[1])
                )

            # Start the test
            elif phase == "Test":
                self.main_window.fill(self.color_scheme['GRAY'])

                # Display stimulus
                question_set_index = question_set.question_set[stimulus_index]
                if not tone_played:  # Prevent looping of the sound
                    self.stimulus(question_set_index, circle_position)
                if question_set_index == "high_tone" or question_set_index == "low_tone":
                    tone_played = True
                else:
                    tone_played = False
                pygame.display.flip()

            # Display EXIT message
            elif phase == "Exit":
                self.main_window.fill(self.color_scheme['GRAY'])

                text_title = title
                title_surface = self.title.render(
                    text=text_title,
                    fgcolor=self.color_scheme['LIGHT_GRAY'],
                    size=self.title.size
                )
                self.main_window.blit(title_surface[0], title_surface[1].move(self.title_pos))

                text_text = "The test is finished."
                text_surface = self.text.render(
                    text=text_text,
                    fgcolor=self.color_scheme['LIGHT_GRAY'],
                    size=self.text.size
                )
                self.main_window.blit(text_surface[0], text_surface[1].move(self.text_pos))

                text_text = f"Test ID:        {score_id}"
                text_surface = self.text.render(
                    text=text_text,
                    fgcolor=self.color_scheme['LIGHT_GRAY'],
                    size=self.text.size
                )
                self.main_window.blit(
                    text_surface[0],
                    text_surface[1].move(self.text_pos[0], self.text_pos[1] + self.text.size * 2.5)
                )

                text_text = f"The results are available at {username}'s profile."
                text_surface = self.text.render(
                    text=text_text,
                    fgcolor=self.color_scheme['LIGHT_GRAY'],
                    size=self.text.size
                )
                self.main_window.blit(
                    text_surface[0],
                    text_surface[1].move(self.text_pos[0], self.text_pos[1] + self.text.size * 3.75)
                )

                text_instr = "PRESS ANY BUTTON TO RETURN TO THE MENU"
                instr_surface = self.instr.render(
                    text=text_instr,
                    fgcolor=self.color_scheme['LIGHT_GRAY'],
                    size=self.instr.size
                )
                self.main_window.blit(
                    instr_surface[0],
                    instr_surface[1].move(self.text_pos[0] + int(self.main_window.get_width()) * 0.5, self.instr_pos[1])
                )
                pygame.display.flip()

            # While loop routine
            pygame.display.update()
            self.clock.tick_busy_loop(self.FPS_ceiling)  # For more accurate display timer


if __name__ == '__main__':
    TestC().run()
