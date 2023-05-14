from Database import user_database
import statistics
from matplotlib import pyplot as plt
from fpdf import FPDF
import subprocess
import os
from Reports.answer_table_generator import create_table, formate_data_for_answer_table
import numpy as np
from sklearn.linear_model import LinearRegression


def _calculate_regression(all_answers):
    # Find linear regression
    model = LinearRegression()

    # Extract absolute times and respond times
    regression_x = []
    regression_y = []
    for answer in all_answers:
        regression_x.append(answer[5])
        regression_y.append(answer[6])
    regression_x = np.array(regression_x).reshape((-1, 1))
    regression_y = np.array(regression_y)
    model.fit(regression_x, regression_y)
    regression = model.intercept_ + model.coef_ * regression_x
    return regression_x, regression


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
        _all_answers = user_database.select_every_answer_for_current_score(score_id)

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
        abs_time_of_correct_answer = []
        respond_time_of_correct_answer = []
        for variable in correct_answers:
            abs_time_of_correct_answer.append(variable[4])
            respond_time_of_correct_answer.append(variable[5])
        incorrect_answers = user_database.select_specific_answers(
            score_id, "Incorrect")
        abs_time_of_incorrect_answer = []
        respond_time_of_incorrect_answer = []
        for variable in incorrect_answers:
            abs_time_of_incorrect_answer.append(variable[4])
            respond_time_of_incorrect_answer.append(variable[5])
        late_answers = user_database.select_specific_answers(
            score_id, "Late")
        abs_time_of_late_answer = []
        respond_time_of_late_answer = []
        for variable in late_answers:
            abs_time_of_late_answer.append(variable[4])
            respond_time_of_late_answer.append(variable[5])
        missed_answers = user_database.select_specific_answers(
            score_id, "Missed")
        abs_time_of_missed_answer = []
        respond_time_of_missed_answer = []
        for variable in missed_answers:
            abs_time_of_missed_answer.append(variable[4])
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
            reaction_time_median = 0

        _regression = _calculate_regression(_all_answers)

        # Create a plot out of the measured data
        detailed_graph, ax1 = plt.subplots()
        ax1.plot(abs_time_of_correct_answer, respond_time_of_correct_answer, "go", markersize=3, label="Correct")
        ax1.plot(abs_time_of_incorrect_answer, respond_time_of_incorrect_answer, "ro", markersize=3, label="Incorrect")
        ax1.plot(abs_time_of_late_answer, respond_time_of_late_answer, "bo", markersize=3, label="Missed")
        ax1.plot(abs_time_of_missed_answer, respond_time_of_missed_answer, "ks", markersize=3, label="Late")
        plt.axhline(y=reaction_time_median, color='m', linewidth=0.5, label="Median")
        plt.plot(_regression[0], _regression[1], color='c', linewidth=0.5, label="Regression")

        # Plot properties
        plt.style.use('seaborn-v0_8-dark-palette')
        plt.minorticks_on()
        ax1.patch.set_edgecolor('black')
        ax1.patch.set_linewidth(1)
        plt.ylabel("Reaction time [ms]")
        plt.xlabel("Test time [s]")
        plt.grid(True)
        ax1.grid(color='k', linewidth=0.5, which='major')
        ax1.grid(color='k', linewidth=0.2, which='minor')
        ax1.legend()

        # plt.show()
        detailed_graph.savefig("Detailed_graph.png")
        # Set Title
        report_title = str(user[2]).upper() + " " + str(user[3]).upper()+"'S" + " DETERMINATION TEST RESULTS"

        # Adjust FPDF header and footer
        class PDF(FPDF):
            border_margin = 4

            # Adjust FPDF header
            def header(self):
                self.set_line_width(0.5)
                self.rect(self.border_margin, self.border_margin,
                          self.w - 2 * self.border_margin, self.h - 2 * self.border_margin, 'f')

            # Adjust FPDF footer
            def footer(self):
                self.set_y(-15)
                self.set_font("Helvetica", "I", 10)
                # Add page number:
                self.cell(0, 10, txt=f"Page {self.page_no()}/{{nb}}", align='C')

        # Create pdf "report" output for selected score
        report_pdf = PDF("P", "mm", "A4")
        report_pdf.set_fill_color(40, 93, 191)
        report_pdf.alias_nb_pages()  # Show total number of pages in the footer ({nb})
        report_pdf.add_page()

        # Print the title
        report_pdf.set_font("Helvetica", "B", 20)
        report_pdf.cell(0, 10, report_title, new_x="LMARGIN", new_y="NEXT", align="C")
        report_pdf.line(0 + report_pdf.border_margin, 25, report_pdf.w-report_pdf.border_margin, 25)

        report_pdf.set_font("Helvetica", size=15)

        # Print data onto the report
        report_pdf.cell(0, 10, txt="", new_x="LMARGIN", new_y="NEXT", align='C')
        report_pdf.cell(62, 10, txt="Participant:" + " " + str(user[2]) + " " + str(user[3]), align='C')
        report_pdf.cell(65, 10, txt="Test Form:" + " " + str(selected_score[2]), align='C')
        report_pdf.cell(65, 10, txt="Date:" + " " + str(selected_score[3]), new_x="LMARGIN", new_y="NEXT", align='C')
        report_pdf.cell(0, 10, txt="", new_x="LMARGIN", new_y="NEXT", align='C')
        report_pdf.cell(0, 10, txt="Number of stimuli: " + str(num_of_stimuli),
                        new_x="LMARGIN", new_y="NEXT", align='C')
        report_pdf.cell(0, 10, txt="Number of reactions: " + str(num_of_reactions),
                        new_x="LMARGIN", new_y="NEXT", align='C')
        report_pdf.cell(0, 10, txt="Correct answers: " + str(num_of_correct_answers),
                        new_x="LMARGIN", new_y="NEXT", align='C')
        report_pdf.cell(0, 10, txt="Incorrect answers: " + str(num_of_incorrect_answers),
                        new_x="LMARGIN", new_y="NEXT", align='C')
        report_pdf.cell(0, 10, txt="Late answers: " + str(num_of_late_answers),
                        new_x="LMARGIN", new_y="NEXT", align='C')
        report_pdf.cell(0, 10, txt="Missed answers: " + str(num_of_missed_answers),
                        new_x="LMARGIN", new_y="NEXT", align='C')
        report_pdf.cell(0, 10, txt="Number of repetitive answers: " + str(num_of_repetitive_answers),
                        new_x="LMARGIN", new_y="NEXT", align='C')
        report_pdf.cell(0, 10, txt="Reaction Time Median: " + str(reaction_time_median) + " ms",
                        new_x="LMARGIN", new_y="NEXT", align='C')

        # Add the graph to the pdf
        report_pdf.image("Detailed_graph.png", x=10, w=report_pdf.w - 20)

        report_pdf.add_page()
        _data = formate_data_for_answer_table(_all_answers)

        # Generate the answer table
        create_table(report_pdf, table_data=_data, title='Answer Table', cell_w='even')

        # Specify the location, where the file is being saved and what name it is going to have
        _project_dir = os.path.join(os.getcwd(), os.pardir)
        _filename = f"{_project_dir}/Reports/DT report-{user[2]} {user[3]}-{selected_score[1]}.pdf"
        # Check if the file already doesn't exist. If exists remove it before generating the new one.
        if os.path.exists(_filename):
            os.remove(_filename)

        # Generate a PDF file and open it
        report_pdf.output(_filename)
        subprocess.Popen(_filename, shell=True)
    except TypeError and PermissionError:
        pass


if __name__ == "__main__":
    print_report_to_pdf(1, 3)
