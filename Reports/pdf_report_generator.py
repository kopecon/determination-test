from Database import user_database
import statistics
from matplotlib import pyplot as plt
from fpdf import FPDF
import subprocess


# Create a PDF report of current test score
def print_report_to_pdf(user_id, score_id):
    # Try fetching data if exists from DT User Database
    try:
        # Get data from User Table
        user = user_database.select_current_user(user_id)

        # Get data from Score Table
        selected_score = user_database.select_current_score(score_id)

        # Get data from Answer Table
        # All answers for current score
        # answers = DT_Database_V2.select_every_answer_for_current_score(current_score_rowid)
        # Total number of specific answers
        num_of_stimuli = user_database.number_of_stimuli(
            score_id)
        num_of_reactions = user_database.number_of_reactions(
            score_id)
        num_of_correct_answers = user_database.number_of_answers(
            score_id, "Correct")
        num_of_incorrect_answers = user_database.number_of_answers(
            score_id, "Incorrect")
        num_of_late_answers = user_database.number_of_answers(
            score_id, "Late")
        num_of_missed_answers = user_database.number_of_answers(
            score_id, "Missed")
        num_of_repetitive_answers = user_database.number_of_answers(
            score_id, "Repeated")
        # List of specific answers
        correct_answers = user_database.select_specific_answers(
            score_id, "Correct")
        absolute_time_of_correct_answer = []
        respond_time_of_correct_answer = []
        for variable in correct_answers:
            absolute_time_of_correct_answer.append(variable[4])
            respond_time_of_correct_answer.append(variable[5])
        incorrect_answers = user_database.select_specific_answers(
            score_id, "Incorrect")
        absolute_time_of_incorrect_answer = []
        respond_time_of_incorrect_answer = []
        for variable in incorrect_answers:
            absolute_time_of_incorrect_answer.append(variable[4])
            respond_time_of_incorrect_answer.append(variable[5])
        late_answers = user_database.select_specific_answers(
            score_id, "Late")
        absolute_time_of_late_answer = []
        respond_time_of_late_answer = []
        for variable in late_answers:
            absolute_time_of_late_answer.append(variable[4])
            respond_time_of_late_answer.append(variable[5])
        missed_answers = user_database.select_specific_answers(
            score_id, "Missed")
        absolute_time_of_missed_answer = []
        respond_time_of_missed_answer = []
        for variable in missed_answers:
            absolute_time_of_missed_answer.append(variable[4])
            respond_time_of_missed_answer.append(variable[5])

        # Calculate Reaction Time Median:
        reactions = user_database.select_every_reaction_for_current_score(
            score_id)
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
