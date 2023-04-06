import pygame
import time

# -----------------------------------------------------------------------------------------  Import Custom Program Code:

from Database import user_database
from Tests import question_set
from Tests.test_environment import TestEnvironment


# ----------------------------------------------------------------------------------------------------------  Functions:
class TestB(TestEnvironment):
    # Printing instance of this class returns the name of this class
    def __repr__(self):
        return __class__.__name__

    # Method that starts the test
    def run(self, phase="Instructions"):
        self.start_pygame()

        test_form = "B"

        # Test title
        title = f"DETERMINATION TEST - {test_form.upper()} FORM"
        pygame.display.set_caption(f"DT Test Form: {test_form}")

        # Declare test variables
        epoch_time = 0
        previous_stimulus_time_ms = 0
        stimulus_delay_time = 1500  # [ms] fixed stimulus time
        reset_respond_time_ms = 0
        current_script_time_ms = 0
        answered = False
        stimulus_index = 0
        answer_type = None
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
                    # Start test by pressing any button/key
                    if phase == "Instructions":
                        phase = "Test"
                        self.main_window.fill(self.color_scheme['GRAY'])
                        pygame.display.flip()
                        time.sleep(stimulus_delay_time / 1000)
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
                        response_time_ns = press_time_ns - reset_respond_time_ms * 1000000

                        # Check for answer properties and insert them to answer table
                        # Correct Answer
                        if event.key == question_set.answer_set[stimulus_index] \
                                and not answered:
                            # Insert correct answer in to answer table
                            answer_type = user_database.insert_into_answer_table(
                                question_set.question_set[stimulus_index],
                                pygame.key.name(event.key),
                                "Correct",
                                current_script_time_ms / 1000,
                                response_time_ns / 1000000,
                                score_id
                            )

                        # Incorrect Answer
                        elif not event.key == question_set.answer_set[stimulus_index] \
                                and not event.key == question_set.answer_set[stimulus_index - 1] \
                                and not answered:

                            # Insert incorrect answer in to answer table
                            answer_type = user_database.insert_into_answer_table(
                                question_set.question_set[stimulus_index],
                                pygame.key.name(event.key),
                                "Incorrect",
                                current_script_time_ms / 1000,
                                response_time_ns / 1000000,
                                score_id
                            )

                        # Late Answer
                        elif not event.key == question_set.answer_set[stimulus_index] \
                                and event.key == question_set.answer_set[stimulus_index - 1] \
                                and not answered:

                            if answer_type == "Missed":
                                # Update missed answer to late answer in answer table
                                answer_type = user_database.update_answer(
                                    question_set.question_set[stimulus_index - 1],
                                    pygame.key.name(event.key),
                                    "Late",
                                    current_script_time_ms / 1000,
                                    response_time_ns / 1000000,
                                    stimulus_index
                                )

                        # Repeated Answer
                        elif answered:

                            # Insert repeated answer in to answer table as incorrect answer
                            answer_type = user_database.insert_into_answer_table(
                                "Repeated Input",
                                pygame.key.name(event.key),
                                "Incorrect",
                                current_script_time_ms / 1000,
                                response_time_ns / 1000000,
                                score_id
                            )
                            # Prevent over clogging of the event queue by spamming answers
                            pygame.event.clear()

                        answered = True

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

                text_text = "Try answering correctly."
                text_surface = self.text.render(
                    text=text_text,
                    fgcolor=self.color_scheme['LIGHT_GRAY'],
                    size=self.text.size
                )
                self.main_window.blit(
                    text_surface[0],
                    text_surface[1].move(self.text_pos[0], self.text_pos[1] + self.text.size * 5)
                )

                text_text = "Tempo of the task assignment is fixed."
                text_surface = self.text.render(
                    text=text_text,
                    fgcolor=self.color_scheme['LIGHT_GRAY'],
                    size=self.text.size
                )
                self.main_window.blit(
                    text_surface[0],
                    text_surface[1].move(self.text_pos[0], self.text_pos[1] + self.text.size * 6.25)
                )

                text_text_5 = f"Test duration:  {len(question_set.question_set) * stimulus_delay_time / 60000}   min"
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
                    instr_surface[1].move(self.instr_pos[0] + int(
                        self.main_window.get_width()) * 0.6, self.instr_pos[1])
                )

            # Start the test
            elif phase == "Test":
                self.main_window.fill(self.color_scheme['GRAY'])

                # Set "time zero" when running the test
                current_script_time_ms = (time.time_ns() - epoch_time) / 1000000

                # Display stimulus
                if not answered:
                    self.main_window.fill(self.color_scheme['GRAY'])
                    question_set_index = question_set.question_set[stimulus_index]
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
                        # Insert missed answer in to answer table
                        answer_type = user_database.insert_into_answer_table(
                            question_set.question_set[stimulus_index],
                            None,
                            "Missed",
                            current_script_time_ms / 1000,
                            0,
                            score_id
                        )

                    # Prepare new random position
                    circle_position = self.random_circle_position()

                    # Clear Event Queue to prevent from reacting before stimulus shown
                    pygame.event.clear()

                    # Next stimulus or finish test if ran out of stimulus
                    if stimulus_index < len(question_set.question_set) - 1:
                        stimulus_index += 1
                    else:
                        self.main_window.fill(self.color_scheme['GRAY'])
                        pygame.display.flip()

                        text_text = "Loading..."
                        title_surface = self.text.render(
                            text=text_text,
                            fgcolor=self.color_scheme['LIGHT_GRAY'],
                            size=self.text.size
                        )
                        self.main_window.blit(
                            title_surface[0],
                            title_surface[1].move(int(self.main_window.get_width()) * 0.44, self.title_pos[1] * 1.5))
                        pygame.display.flip()

                        time.sleep(2)

                        self.main_window.fill(self.color_scheme['GRAY'])
                        pygame.display.flip()

                        phase = "Exit"

                    # Reset stimulus time
                    previous_stimulus_time_ms = (time.time_ns() - epoch_time) / 1000000
                    # Reset reaction time if answered
                    if answered:
                        reset_respond_time_ms = previous_stimulus_time_ms
                    answered = False

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
                self.main_window.blit(text_surface[0], text_surface[1].move(self.title_pos))

                text_text = f"Test ID:        {score_id}"
                text_surface = self.text.render(
                    text=text_text,
                    fgcolor=self.color_scheme['LIGHT_GRAY'],
                    size=self.text.size
                )
                self.main_window.blit(
                    text_surface[0],
                    text_surface[1].move(self.title_pos[0], self.title_pos[1] + self.text.size * 2.5)
                )

                text_text = f"The results are available at {username}'s profile."
                text_surface = self.text.render(
                    text=text_text,
                    fgcolor=self.color_scheme['LIGHT_GRAY'],
                    size=self.text.size
                )
                self.main_window.blit(
                    text_surface[0],
                    text_surface[1].move(self.title_pos[0], self.title_pos[1] + self.text.size * 3.75)
                )

                text_instr = "PRESS ANY BUTTON TO RETURN TO THE MENU"
                instr_surface = self.instr.render(
                    text=text_instr,
                    fgcolor=self.color_scheme['LIGHT_GRAY'],
                    size=self.instr.size
                )
                self.main_window.blit(
                    instr_surface[0],
                    instr_surface[1].move(
                        self.title_pos[0] + int(self.main_window.get_width()) * 0.5, self.instr_pos[1])
                )
                pygame.display.flip()

            # While loop routine
            pygame.display.update()
            self.clock.tick_busy_loop(self.FPS_ceiling)  # For more accurate display timer


if __name__ == '__main__':
    TestB().run()
