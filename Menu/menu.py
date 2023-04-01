from kivy.app import App
from kivy.core.text import LabelBase
from kivy.lang import Builder
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.core.window import Window
from datetime import datetime
from matplotlib import pyplot as plt
from fpdf import FPDF
import subprocess
import random
import statistics

# --------------------------------------------------------------------------------------      Import Custom Program Code
from Database import user_database
from Tests.test_a import TestA
from Tests.test_b import TestB
from Tests.test_c import TestC
from Tests.instructions import Instructions


# ---------------------------------------------------------------------------------      Used variables (not adjustable)
no_user_popup = Popup(title="Reminder", content=Label(text="No User Selected"), size_hint=(None, None), size=(200, 100))


# -------------------------------------------------------------------------------------------------------      Functions
# Create a function that allows reopening window after closing it
# solution by: https://stackoverflow.com/questions/68697821/can-i-close-kivy-window-and-open-it-again
def reset():
    import kivy.core.window as window
    from kivy.base import EventLoop
    if not EventLoop.event_listeners:
        from kivy.cache import Cache
        window.Window = window.core_select_lib('window', window.window_impl, True)
        # noinspection PyProtectedMember
        for cat in Cache._categories:
            # noinspection PyProtectedMember
            Cache._objects[cat] = {}


# -------------------------------------------------------------------------------      Load a layout style form .kv file
LabelBase.register(name='Ardestine',
                   fn_regular='Style/Fonts/Ardestine.ttf')
LabelBase.register(name='D-DINCondensed',
                   fn_regular='Style/Fonts/D-DINCondensed-Bold.ttf')
LabelBase.register(name='Montserrat-SemiBold',
                   fn_regular='Style/Fonts/Montserrat-SemiBold.ttf')

Builder.load_file("Style/menu_layout.kv")


# --------------------------------------------------------------------------------------------------      Define Classes

# Setup Classes for Recycle View by Kivy:
# https://kivy.org/doc/stable/api-kivy.uix.recycleview.html?highlight=recycle%20view#module-kivy.uix.recycleview

# Create a layout with selectable labels
class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout):
    touch_deselect_last = BooleanProperty(True)
    pass


# Process the selecting of label representing specific user
class UserSelectableLabel(RecycleDataViewBehavior, BoxLayout):
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    # Update data from selected label
    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        return super(UserSelectableLabel, self).refresh_view_attrs(rv, index, data)

    # Check for pressing label
    def on_touch_down(self, touch):
        if super(UserSelectableLabel, self).on_touch_down(touch):
            return True

        if self.collide_point(*touch.pos) and self.selectable:
            if touch.is_double_tap:
                Menu.main_screen.go_to_user_records()
            return self.parent.select_with_touch(self.index, touch)

    # Connect selected label to its database reference and get its user's id
    def apply_selection(self, rv, index, is_selected):
        self.selected = is_selected
        if is_selected:
            # Fetch the data of the selected user from the user database
            selected_user = user_database.select_current_user(rv.data[index]['user_id'])

            # Update the :Menu.current_user: instance
            Menu.current_user = User(int(selected_user[0]), str(selected_user[2]), str(selected_user[3]),
                                     int(selected_user[4]), str(selected_user[5]), str(selected_user[6]), True)

        if not is_selected:
            # Reset the :Menu.current_user: instance
            Menu.current_user = User(None, None, None, None, None, None, False)


# Process the selecting of label representing specific score
class ScoreSelectableLabel(RecycleDataViewBehavior, BoxLayout):
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    # Update data from selected label
    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        return super(ScoreSelectableLabel, self).refresh_view_attrs(rv, index, data)

    # Check for pressing label
    def on_touch_down(self, touch):
        if super(ScoreSelectableLabel, self).on_touch_down(touch):
            return True

        if self.collide_point(*touch.pos) and self.selectable:
            if touch.is_double_tap:
                Menu.user_records_screen.get_report()
            return self.parent.select_with_touch(self.index, touch)

    # Connect selected label to its database reference and get its user's id
    def apply_selection(self, rv, index, is_selected):
        self.selected = is_selected
        if is_selected:
            # Fetch the data of the selected score from the user database
            selected_score = user_database.select_current_score(rv.data[index]['label_0'])

            # Update the :Menu.current_user.current_score: instance
            Menu.current_user.current_score = Score(int(selected_score[4]), int(selected_score[0]),
                                                    str(selected_score[2]), str(selected_score[3]), True)

        if not is_selected:
            # Reset :Menu.current_user.current_score: instance
            Menu.current_user.current_score = Score(None, None, None, None, False)


# Create the Intro screen
class IntroScreen(Screen):
    # Find selected input device
    @staticmethod
    def select_input_device(input_device_val):
        Menu.input_device.device_type = input_device_val


class InputDeviceIP(Screen):
    def submit_ip_address(self):
        Menu.input_device.device_ip = str(self.ids.input_device_ip_text_input_id.text)


# Create Main Menu Screen
class MainScreen(TabbedPanel, Screen):
    form_A_button_id = ObjectProperty(None)
    form_B_button_id = ObjectProperty(None)
    form_C_button_id = ObjectProperty(None)
    profile_tab = ObjectProperty(None)
    test_tab = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        pass

    # Update list of users on entering the screen "List of Users"
    def on_enter(self, *args):
        self.ids.user_list_view.refresh_view()

    @staticmethod
    def go_to_user_records():
        App.get_running_app().root.transition.direction = "left"
        App.get_running_app().root.current = "User Records"

    # Delete selected user
    def delete_user(self):
        # Get the ID of the selected user, who is going to be deleted
        user_id = Menu.current_user.user_id

        # Delete every score for the current user
        for score in user_database.select_every_score_for_current_user(user_id):
            score_id = score[0]
            user_database.delete_answers(score_id)  # Delete all the answers from the current score
            user_database.delete_score(score_id)  # Delete the current score
        user_database.delete_user(user_id)  # Delete the user
        Menu.current_user.is_selected = False  # No user is selected
        self.ids.user_list_view.refresh_view()  # Refresh the list of users

    def start_test(self):
        # Start Test Form A
        if self.ids.form_A_button_id.state == "down" and Menu.current_user.is_selected:
            App.get_running_app().stop()
            Window.close()
            # Start with instructions
            if self.ids.instruction_checkbox.state == "down":
                result = Instructions().run()

                if result == "Success":
                    TestA().run()

            # Start without instructions
            else:
                TestA().run()

            # Reopen Menu Tab
            reset()
            Menu().run()

        # Start Test Form B
        elif self.ids.form_B_button_id.state == "down" and Menu.current_user.is_selected:
            App.get_running_app().stop()
            Window.close()
            # Start with instructions
            if self.ids.instruction_checkbox.state == "down":
                result = Instructions().run()

                if result == "Success":
                    TestB().run()

            # Start without instructions
            else:
                TestB().run()

            # Reopen Menu Tab
            reset()
            Menu().run()

        # Start Test Form C
        elif self.ids.form_C_button_id.state == "down" and Menu.current_user.is_selected:
            App.get_running_app().stop()
            Window.close()
            # Start with instructions
            if self.ids.instruction_checkbox.state == "down":
                result = Instructions().run()

                if result == "Success":
                    TestC().run()

            # Start without instructions
            else:
                TestC().run()
            # Reopen Menu Tab
            reset()
            Menu().run()

        # Remind user selection
        elif not Menu.current_user.is_selected:
            no_user_popup.open()
            self.switch_to(self.profile_tab)


# Create a List of Users
class UsersRV(RecycleView):
    def __init__(self, **kwargs):
        super(UsersRV, self).__init__(**kwargs)

    def refresh_view(self):
        user_database.create_user_table()
        user_database.create_score_table()
        user_database.create_answer_table()
        user_database.select_all_users()
        user_records = user_database.select_all_users()

        # Extract data from "DTUserDatabase.db" to create Selectablelabels with users in "List of Users" screen
        self.data = [{
            'order': str(iteration + 1), 'firstname': str(user[2]), 'surname': str(user[3]), 'user_id': str(user[0])
        } for iteration, user in enumerate(user_records)]


# Create a List of User Records
class UserRecordsRV(RecycleView):
    def __init__(self, **kwargs):
        super(UserRecordsRV, self).__init__(**kwargs)

    def refresh_view(self):
        user_database.create_user_table()
        user_database.create_score_table()
        user_database.create_answer_table()
        user_database.select_all_users()
        score_records = user_database.select_every_score_for_current_user(Menu.current_user.user_id)

        # Extract data from "DTUserDatabase.db" to create Selectablelabels with scores in "User Records" screen
        self.data = [{'label_0': str(score[1]),
                      'label_3': str(score[2]),
                      'label_4': str(score[3])
                      } for iteration, score in enumerate(score_records)]


# Create a User Records List Screen
class UserRecords(TabbedPanel, Screen):
    @staticmethod
    def link_to_start_test():
        Menu.main_screen.start_test()

    # Update list of users on entering the screen "List of Users"
    def on_enter(self, *args):
        self.ids.user_records_view.refresh_view()

    # Create a PDF report of current test score
    def get_report(self):
        # Try fetching data if exists from DT User Database
        try:
            # Get data from User Table
            user = user_database.select_current_user(Menu.current_user.user_id)

            # Get data from Score Table
            selected_score = user_database.select_current_score(Menu.current_user.current_score.score_id)

            # Get data from Answer Table
            # All answers for current score
            # answers = DT_Database_V2.select_every_answer_for_current_score(current_score_rowid)
            # Total number of specific answers
            num_of_stimuli = user_database.number_of_stimuli(
                Menu.current_user.current_score.score_id)
            num_of_reactions = user_database.number_of_reactions(
                Menu.current_user.current_score.score_id)
            num_of_correct_answers = user_database.number_of_answers(
                Menu.current_user.current_score.score_id, "Correct")
            num_of_incorrect_answers = user_database.number_of_answers(
                Menu.current_user.current_score.score_id, "Incorrect")
            num_of_late_answers = user_database.number_of_answers(
                Menu.current_user.current_score.score_id, "Late")
            num_of_missed_answers = user_database.number_of_answers(
                Menu.current_user.current_score.score_id, "Missed")
            num_of_repetitive_answers = user_database.number_of_answers(
                Menu.current_user.current_score.score_id, "Repeated")
            # List of specific answers
            correct_answers = user_database.select_specific_answers(
                Menu.current_user.current_score.score_id, "Correct")
            absolute_time_of_correct_answer = []
            respond_time_of_correct_answer = []
            for variable in correct_answers:
                absolute_time_of_correct_answer.append(variable[4])
                respond_time_of_correct_answer.append(variable[5])
            incorrect_answers = user_database.select_specific_answers(
                Menu.current_user.current_score.score_id, "Incorrect")
            absolute_time_of_incorrect_answer = []
            respond_time_of_incorrect_answer = []
            for variable in incorrect_answers:
                absolute_time_of_incorrect_answer.append(variable[4])
                respond_time_of_incorrect_answer.append(variable[5])
            late_answers = user_database.select_specific_answers(
                Menu.current_user.current_score.score_id, "Late")
            absolute_time_of_late_answer = []
            respond_time_of_late_answer = []
            for variable in late_answers:
                absolute_time_of_late_answer.append(variable[4])
                respond_time_of_late_answer.append(variable[5])
            missed_answers = user_database.select_specific_answers(
                Menu.current_user.current_score.score_id, "Missed")
            absolute_time_of_missed_answer = []
            respond_time_of_missed_answer = []
            for variable in missed_answers:
                absolute_time_of_missed_answer.append(variable[4])
                respond_time_of_missed_answer.append(variable[5])

            # Calculate Reaction Time Median:
            reactions = user_database.select_every_reaction_for_current_score(
                Menu.current_user.current_score.score_id)
            reaction_times = []
            for variable in reactions:
                reaction_times.append(variable[6])

            # Prevent no data error for statistics.median
            try:
                reaction_time_median = round(statistics.median(reaction_times), 3)
            except statistics.StatisticsError:
                reaction_time_median = None

            # Create a plot out of the measured data
            plt.style.use("seaborn-dark")
            detailed_graph, ax1 = plt.subplots()
            ax1.plot(absolute_time_of_correct_answer, respond_time_of_correct_answer, "go", markersize=2)
            ax1.plot(absolute_time_of_incorrect_answer, respond_time_of_incorrect_answer, "ro", markersize=2)
            ax1.plot(absolute_time_of_late_answer, respond_time_of_late_answer, "bo", markersize=2)
            ax1.plot(absolute_time_of_missed_answer, respond_time_of_missed_answer, "ks", markersize=2)
            # plt.show()
            detailed_graph.savefig("Detailed_graph.png")
            # Set Title
            title = str(user[2]) + " " + str(user[3]) + " DETERMINATION TEST RESULTS"

            # Adjust FPDF header and footer
            class PDF(FPDF):
                # Adjust FPDF header
                def header(self):
                    self.set_font("Times", "B", 20)

                    # Get width of the title
                    title_width = self.get_string_width(title) + 10

                    # Center the title
                    page_width = self.w
                    self.set_x((page_width - title_width) / 2)

                    # Insert Title
                    self.cell(title_width, 10, title, ln=1, align="C")

                # Adjust FPDF footer
                def footer(self):
                    self.set_y(-15)
                    self.set_font("Times", "I", 10)
                    # Add page number:
                    self.cell(0, 10, txt=f"Page {self.page_no()}/{{nb}}", align='C')

            # Create pdf "report" output for selected score
            report_pdf = PDF("P", "mm", "A4")
            report_pdf.add_page()
            report_pdf.set_font("Times", size=15)

            # Print data onto the report
            report_pdf.cell(0, 10, txt="Participant:" + " " + str(user[2]) + " " + str(user[3]), ln=1, align='C')
            report_pdf.cell(0, 10, txt="Test Form:" + " " + str(selected_score[2]), ln=1, align='C')
            report_pdf.cell(0, 10, txt="Date:" + " " + str(selected_score[3]), ln=1, align='C')
            report_pdf.cell(0, 10, txt="", ln=1, align='C')
            report_pdf.cell(0, 10, txt="Number of stimuli: " + str(num_of_stimuli), ln=1, align='C')
            report_pdf.cell(0, 10, txt="Number of reactions: " + str(num_of_reactions), ln=1, align='C')
            report_pdf.cell(0, 10, txt="Correct answers: " + str(num_of_correct_answers), ln=1, align='C')
            report_pdf.cell(0, 10, txt="Incorrect answers: " + str(num_of_incorrect_answers), ln=1, align='C')
            report_pdf.cell(0, 10, txt="Late answers: " + str(num_of_late_answers), ln=1, align='C')
            report_pdf.cell(0, 10, txt="Missed answers: " + str(num_of_missed_answers), ln=1, align='C')
            report_pdf.cell(0,
                            10,
                            txt="Number of repetitive answers: " + str(num_of_repetitive_answers),
                            ln=1,
                            align='C')
            report_pdf.cell(0, 10, txt="Reaction Time Median: " + str(reaction_time_median) + " ms", ln=1, align='C')

            report_pdf.image("Detailed_graph.png", x=10, w=report_pdf.w - 20)

            # Generate a PDF file and open it
            report_pdf.output(f"DT report-{user[2]} {user[3]}-{selected_score[1]}.pdf", dest="F")
            subprocess.Popen([f"DT report-{user[2]} {user[3]}-{selected_score[1]}.pdf"], shell=True)
        except TypeError and PermissionError:
            pass

    def delete_score(self):
        score_id = Menu.current_user.current_score.score_id
        user_database.delete_answers(score_id)
        user_database.delete_score(score_id)
        Menu.current_user.current_score.is_selected = False
        self.ids.user_records_view.refresh_view()


# Create a User Creation Screen
class UserCreator(TabbedPanel, Screen):
    def on_enter(self, *args):
        # Erase input fields
        self.ids.first_name_input.text = ""
        self.ids.surname_input.text = ""
        self.ids.age_input.text = ""
        self.ids.profession_input.text = ""
        self.ids.nationality_input.text = ""

    def create_user(self):
        firstname = self.ids.first_name_input.text
        surname = self.ids.surname_input.text
        age = self.ids.age_input.text
        profession = self.ids.profession_input.text
        nationality = self.ids.nationality_input.text
        user_database.insert_into_user_table(firstname, surname, age, profession, nationality)
        # Erase the input fields
        self.ids.first_name_input.text = ""
        self.ids.surname_input.text = ""
        self.ids.age_input.text = ""
        self.ids.profession_input.text = ""
        self.ids.nationality_input.text = ""

    @staticmethod
    def create_dummy_user():
        surname = str(random.randint(0, 20))
        user_database.insert_into_user_table("DUMMY", surname, "0", "None", "Uganda")

    def create_dummy_score(self):
        if Menu.current_user.is_selected:
            score_id = user_database.insert_into_score_table(
                "DUMMY SCORE",
                datetime.now().strftime("%d/%m/%Y %H:%M"),
                Menu.current_user.user_id
            )

            # Generate one answer per one absolute time
            used_time = []
            absolute_time = 0
            answer_types = ["Correct", "Incorrect", "Missed", "Late", "Repeated"]

            # Generate fake answers
            for i in range(16):
                while absolute_time in used_time:  # Make sure to use only that absolute time which has not been used
                    absolute_time = random.uniform(0.0, 12.0)

                # Insert fake answers to the created score
                user_database.insert_into_answer_table(
                    f"Who asked? {i}",
                    f"Yo Mum {i}", random.choice(answer_types), absolute_time, random.uniform(0.0, 500), score_id)

                used_time.append(absolute_time)  # Mark this absolute time as used

        # Remind user selection
        elif not Menu.current_user.is_selected:
            no_user_popup.open()
            self.manager.transition.direction = "right"


# Class representing the score that is being modified
class Score:
    def __init__(self, user_id, score_id, test_form, date, is_selected):
        self.user_id = user_id
        self.score_id = score_id
        self.test_form = test_form
        self.date = date
        self.is_selected = is_selected

    def __repr__(self):
        score_description = f'''
        User ID: {self.user_id}
        Score ID: {self.score_id}
        Test form: {self.test_form}
        Date: {self.date}
        Selected: {self.is_selected}
        '''
        return score_description


# Class representing the user that is being modified
class User:
    def __init__(self, user_id=None, first_name=None, surname=None, age=None, profession=None, nationality=None,
                 is_selected=False):

        self.user_id = user_id
        self.first_name = first_name
        self.surname = surname
        self.user_name = f"{self.first_name} {self.surname}"
        self.age = age
        self.profession = profession
        self.nationality = nationality
        self.current_score = Score(None, None, None, None, False)
        self.is_selected = is_selected

    def __repr__(self):
        user_description = f'''
        Username: {self.user_name}
        User ID: {self.user_id}
        '''
        return user_description


# Class representing the device that is being used to control the test
class Device:
    def __init__(self, device_type="KEYBOARD"):
        self.device_type = device_type
        self.device_ip = None


# -------------------------------------------------------------------------------      Define the main application class
class Menu(App):
    # Selected user, who is being modified
    current_user = User(None)
    # Used device properties
    input_device = Device()

    # Screen instances
    user_records_screen = UserRecords(name="User Records")
    main_screen = MainScreen(name="Main Screen")
    user_creator_screen = UserCreator(name="User Creator")

    def build(self):
        Window.size = (500, 750)
        Window.clearcolor = (40 / 255, 93 / 255, 191 / 255, 0.6)
        # Create the Screen Manager
        sm = ScreenManager(transition=NoTransition())
        sm.add_widget(IntroScreen(name="Intro Screen"))
        sm.add_widget(InputDeviceIP(name="Input Device IP Screen"))
        sm.add_widget(MainScreen(name="Main Screen"))
        sm.add_widget(UserRecords(name="User Records"))
        sm.add_widget(UserCreator(name="User Creator"))
        self.title = "DT Menu"
        return sm


# --------------------------------------------------------------------------------------------      Run Menu Application

if __name__ == '__main__':
    Menu().run()
