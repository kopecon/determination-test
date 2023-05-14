from kivy.app import App
from kivy.core.text import LabelBase
from kivy.lang import Builder
from kivy.properties import BooleanProperty
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
import random

# ------------------------------------------------------------------------------------------  Import Custom Program Code
from Database import user_database
from Tests.test_a import TestA
from Tests.test_b import TestB
from Tests.test_c import TestC
from Tests.instructions import Instructions
from Reports.pdf_report_generator import print_report_to_pdf

# ---------------------------------------------------------------------------------      Used variables (not adjustable)
no_user_popup = Popup(title="Reminder", content=Label(text="No User Selected"), size_hint=(None, None), size=(200, 100))
no_test_popup = Popup(title="Reminder", content=Label(text="No Test Selected"), size_hint=(None, None), size=(200, 100))


# -----------------------------------------------------------------------------------------------------------  Functions
# Create a function that allows reopening window after closing it
# solution by: https://stackoverflow.com/questions/68697821/can-i-close-kivy-window-and-open-it-again
def _reset():
    import kivy.core.window as window
    from kivy.base import EventLoop
    if not EventLoop.event_listeners:
        from kivy.cache import Cache
        window.Window = window.core_select_lib('window', window.window_impl, True)
        # noinspection PyProtectedMember
        for cat in Cache._categories:
            # noinspection PyProtectedMember
            Cache._objects[cat] = {}


def _screen_ids(screen_name: str):
    """
    Shortcut function that helps with getting the ids of the desired screen

    :param screen_name: Name of the screen which you want to access
    :return: ids of the accessed screen
    """
    return App.get_running_app().root.get_screen(screen_name).ids


# -----------------------------------------------------------------------------------  Load a layout style form .kv file
LabelBase.register(name='Ardestine',
                   fn_regular='Style/Fonts/Ardestine.ttf')
LabelBase.register(name='D-DINCondensed',
                   fn_regular='Style/Fonts/D-DINCondensed-Bold.ttf')
LabelBase.register(name='Montserrat-SemiBold',
                   fn_regular='Style/Fonts/Montserrat-SemiBold.ttf')

Builder.load_file("Style/menu_layout.kv")


# -------------------------------------------------------------------------------------------------------------  Classes

# Setup Classes for Recycle View by Kivy:
# https://kivy.org/doc/stable/api-kivy.uix.recycleview.html?highlight=recycle%20view#module-kivy.uix.recycleview

# Create a layout with selectable labels
class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout):
    touch_deselect_last = BooleanProperty(True)  # FIXME allowing deselection causes issues with double touch.
    pass


# Class that gives selectable option to user labels
class UserSelectableLabel(RecycleDataViewBehavior, BoxLayout):
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    # Update data from selected label
    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        return super(UserSelectableLabel, self).refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        if super(UserSelectableLabel, self).on_touch_down(touch):
            return True

        if self.collide_point(*touch.pos) and self.selectable:
            if touch.is_double_tap:
                # Redirect user to the "User Records Screen"
                App.get_running_app().root.transition.direction = "left"
                App.get_running_app().root.current = "User Records Screen"
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        self.selected = is_selected
        user_id = rv.data[index]['user_id']  # Get the id of the user based on the selected user label

        if is_selected:
            App.get_running_app().selected_user.is_selected = True
            App.get_running_app().selected_user.set_user(user_id)

        if not is_selected:
            # Reset the :App.get_running_app().current_user: instance
            App.get_running_app().selected_user = User(None)


# Create a List of User labels
class UsersRV(RecycleView):
    def __init__(self, **kwargs):
        super(UsersRV, self).__init__(**kwargs)

    def refresh_view(self):
        user_database.connect()
        user_database.select_all_users()
        user_records = user_database.select_all_users()

        # Extract data from "DTUserDatabase.db" to create Selectablelabels with users in "List of Users" screen
        self.data = [{
            'order': str(iteration + 1), 'firstname': str(user[2]), 'surname': str(user[3]), 'user_id': str(user[0])
        } for iteration, user in enumerate(user_records)]


# Class that gives selectable option to score labels
class ScoreSelectableLabel(RecycleDataViewBehavior, BoxLayout):
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    # Update data from selected label
    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        return super(ScoreSelectableLabel, self).refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        if super(ScoreSelectableLabel, self).on_touch_down(touch):
            return True

        if self.collide_point(*touch.pos) and self.selectable:
            if touch.is_double_tap:
                print_report_to_pdf(App.get_running_app().selected_user.user_id,
                                    App.get_running_app().selected_user.selected_score.score_id)
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        self.selected = is_selected
        score_id = rv.data[index]['label_0']  # Get the id of the score based on the selected score label
        if is_selected:
            App.get_running_app().selected_user.selected_score.is_selected = True
            App.get_running_app().selected_user.selected_score.set_score(score_id)

        if not is_selected:
            # Reset :App.get_running_app().current_user.current_score: instance
            App.get_running_app().selected_user.selected_score = Score(
                App.get_running_app().selected_user.user_id, None)


# Create a List of score labels
class ScoreRV(RecycleView):
    def __init__(self, **kwargs):
        super(ScoreRV, self).__init__(**kwargs)

    def refresh_view(self):
        user_database.connect()
        user_database.select_all_users()
        score_records = user_database.select_every_score_for_current_user(App.get_running_app().selected_user.user_id)

        # Extract data from "DTUserDatabase.db" to create Selectablelabels with scores in "User Records" screen
        self.data = [{'label_0': str(score[1]),
                      'label_3': str(score[2]),
                      'label_4': str(score[3])
                      } for iteration, score in enumerate(score_records)]


# Create the Intro screen
class DeviceScreen(Screen):
    # Find selected input device
    @staticmethod
    def select_input_device(input_device_val):
        App.get_running_app().input_device.device_type = input_device_val


# Create a screen where user fills in the device IP (if using the control panel)
class DeviceIPScreen(Screen):
    def submit_ip_address(self):
        App.get_running_app().input_device.device_ip = str(self.ids.input_device_ip_text_input_id.text)


# Screen with USERS/TESTS tabs
class MainScreen(TabbedPanel, Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        pass

    # Update list of users when entering the Main Screen
    def on_enter(self, *args):
        self.ids.user_list_view.refresh_view()

    # Delete selected user
    def delete_user(self):
        # Get the ID of the selected user, who is going to be deleted
        user_id = App.get_running_app().selected_user.user_id

        # Delete every score for the current user
        for score in user_database.select_every_score_for_current_user(user_id):
            score_id = score[0]
            user_database.delete_answers(score_id)  # Delete all the answers from the current score
            user_database.delete_score(score_id)  # Delete the current score
        user_database.delete_user(user_id)  # Delete the user
        App.get_running_app().selected_user.is_selected = False  # No user is selected
        self.ids.user_list_view.refresh_view()  # Refresh the list of users


class ConfigurationScreen(Screen):
    test_mode = False
    mode = f"Test Mode: {test_mode}"

    def test_mode_button(self):
        if App.get_running_app().test is not None:

            self.test_mode = not self.test_mode
            if self.test_mode:
                self.mode = f"Test Mode: {self.test_mode}"
            else:
                self.mode = f"Test Mode: {self.test_mode}"
            self.ids.test_mode_button.text = self.mode

            if App.get_running_app().test.test_name == "ADAPTIVE TEST":
                if self.test_mode:
                    App.get_running_app().test.test_duration = 240000 / 20

            elif App.get_running_app().test.test_name == "REACTIVE TEST":
                if self.test_mode:
                    App.get_running_app().test.number_of_stimuli = 10

            elif App.get_running_app().test.test_name == "ACTIVE TEST":
                if self.test_mode:
                    App.get_running_app().test.number_of_stimuli = 10


# Create a User Records List Screen
class UserRecordsScreen(TabbedPanel, Screen):

    # Update list of users on entering the screen "List of Users"
    def on_enter(self, *args):
        self.ids.user_records_view.refresh_view()

    # Method that deletes selected score
    def delete_score(self):
        score_id = App.get_running_app().selected_user.selected_score.score_id
        user_database.delete_answers(score_id)
        user_database.delete_score(score_id)
        App.get_running_app().selected_user.selected_score.is_selected = False
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
        # Save data written in the input rows
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

    @staticmethod
    def create_dummy_score():
        if App.get_running_app().selected_user.is_selected:
            score_id = user_database.insert_into_score_table(
                "DUMMY SCORE",
                datetime.now().strftime("%d/%m/%Y %H:%M"),
                App.get_running_app().selected_user.user_id
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
        elif not App.get_running_app().selected_user.is_selected:
            no_user_popup.open()


# Class representing the score that is being modified
class Score:
    def __init__(self, user_id, score_id=None):
        self.user_id = user_id
        self.score_id = score_id
        self.score_data = {}
        self.set_score(score_id)
        self.is_selected = False

    # Fetch the data for the selected score from the user database
    def set_score(self, score_id):

        score_in_db = user_database.select_current_score(score_id)  # Look for the score in user database

        if score_in_db is not None:
            self.score_id = score_in_db[0]
            self.score_data = {'test_form': score_in_db[2], 'date': score_in_db[3]}
        return

    def __repr__(self):
        score_description = f'''
        User ID: {self.user_id}
        Score ID: {self.score_id}
        Test form: {self.score_data['test_form']}
        Date: {self.score_data['date']}
        '''
        return score_description


# Class representing the user that is being modified
class User:
    """
    Current user is pulled from the "user_database.db" everytime a label in the user list is selected.
    Users attributes are set based on the id of the user in the database matched with the id of the selected label.
    """

    def __init__(self, user_id=None):
        self.user_id = user_id  # This is the most important attribute of the user
        self.user_data = {}
        self.user_name = None
        self.set_user(user_id)
        self.selected_score = Score(user_id, None)
        self.is_selected = False

    # Fetch the data for the current user from the user database
    def set_user(self, user_id):

        user_in_db = user_database.select_current_user(user_id)  # Look for the user in the database

        # Set user data if the user is found in the database
        if user_in_db is not None:
            self.user_id = user_in_db[0]
            self.user_data = {
                'first_name': user_in_db[2],
                'surname': user_in_db[3],
                'age': user_in_db[4],
                'profession': user_in_db[5],
                'nationality': user_in_db[6]}
            self.user_name = f"{self.user_data['first_name']} {self.user_data['surname']}"
        return

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


# Class that holds all the Test options for easier access
class Tests:
    test_a = TestA
    test_b = TestB
    test_c = TestC


# ----------------------------------------------------------------------------------------------  Main application class
class Menu(App):
    # Selected user, who is being modified (this value is modified when the user selects any row in user tab)
    selected_user = User(None)

    # Used device properties
    input_device = Device()

    # Selected test form
    test = None
    instructions = None

    # Screen instances
    # records_screen = UserRecordsScreen(name="User Records Screen")
    # main_screen = MainScreen(name="Main Screen")
    # user_creator_screen = UserCreator(name="User Creator Screen")

    # Method that assigns the selected test as the current test
    def select_test(self, test_form, checkbox, value):
        _ = checkbox  # Throw away unused argument passed by the pressed radio button
        if value:
            # Assign the current test based on the selected radiobutton
            self.test = (getattr(Tests, test_form))()
            _screen_ids("Main Screen").test_info.text = self.test.test_info
            _screen_ids("Configuration Screen").config_test_name.text = self.test.test_name
        else:
            self.test = None

    # Method that is called when start button is pressed -> starts the instructions before the selected test
    def include_instructions(self, checkbox, value):
        _ = checkbox  # Throw away unused argument passed by the pressed radio button
        if value:
            self.instructions = Instructions()
        else:
            self.instructions = None

    # Method that is called when start button is pressed -> starts the selected test
    def start_test(self):
        # Remind test selection
        if self.test is None:
            no_test_popup.open()
            return
        else:
            self.test.device = self.input_device  # Set the selected device for the upcoming test

        # Remind user selection
        if not self.selected_user.is_selected:
            no_user_popup.open()
            return
        else:
            self.test.current_user = self.selected_user  # Test answers will be recorded for the selected user

        # User and test is selected
        App.get_running_app().stop()
        Window.close()

        # Set user and input device for the upcoming test
        self.test.selected_user = self.selected_user
        self.test.device = self.input_device

        # If user included instructions start instructions first
        if self.instructions is not None:
            result = self.instructions.run()

            # Start the test if the user passed the instructions
            if result == "Success":
                self.test.run()

            # Repeat starting the test process if the user didn't pass the instructions
            else:
                self.start_test()

        else:
            self.test.run()

        # Reopen Menu Tab
        _reset()
        Menu().run()

    def build(self):
        # Setup window
        Window.size = (500, 750)
        Window.clearcolor = (40 / 255, 93 / 255, 191 / 255, 0.6)
        # Create the Screen Manager
        sm = ScreenManager(transition=NoTransition())
        sm.add_widget(DeviceScreen(name="Intro Screen"))
        sm.add_widget(DeviceIPScreen(name="Input Device IP Screen"))
        sm.add_widget(MainScreen(name="Main Screen"))
        sm.add_widget(UserRecordsScreen(name="User Records Screen"))
        sm.add_widget(UserCreator(name="User Creator Screen"))
        sm.add_widget(ConfigurationScreen(name="Configuration Screen"))
        self.title = "DT Menu"
        return sm


# ------------------------------------------------------------------------------------------------  Run Menu Application
if __name__ == '__main__':
    Menu().run()
