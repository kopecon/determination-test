import sqlite3
import os

# ----------------------          Adjustable parameters         --------------------------------------------------------
database_name = "user_database.db"                       # Choose your Database file to store user's data (*.db file)

# ----------------------      Used variables (not adjustable)      -----------------------------------------------------
user_records = []
user_total = 0


# -------------------------------------------------------------------------------------------   Connect to the Database:
# Create a function to connect to User Database
def connect_to_user_db():
    # Specify the location where to save the .db file
    project_dir = os.path.join(os.getcwd(), os.pardir)                         # Get the parent of the current directory
    database_dir = f'{project_dir}/Database/'                                           # Path to the database directory

    # Connect or create connection to User Database
    conn = sqlite3.connect(f'{database_dir}{database_name}')       # Database '.db' is located in the Database directory
    return conn


# -----------------------------------------------------------------------------------------------------   Create Tables:
# Create a function to create a user table
def create_user_table():
    conn = connect_to_user_db()
    c = conn.cursor()

    c.execute("""CREATE TABLE if not exists UserTable(
                CustomUserID INTEGER PRIMARY KEY NOT NULL, 
                Firstname TEXT NOT NULL, 
                Surname TEXT NOT NULL, 
                Age INTEGER NOT NULL, 
                Profession TEXT, 
                Nationality TEXT
                )""")
    conn.commit()
    conn.close()


# Create a function to create a score table
def create_score_table():
    conn = connect_to_user_db()
    c = conn.cursor()

    c.execute("""CREATE TABLE if not exists ScoreTable(
                CustomScoreID INTEGER PRIMARY KEY NOT NULL,
                TestForm TEXT NOT NULL,
                Date INTEGER NOT NULL,
                UserID INTEGER NOT NULL,
                FOREIGN KEY(UserID) REFERENCES UserTable(CustomUserID)
                )""")

    conn.commit()
    conn.close()


# Create a function to create an answer table
def create_answer_table():
    conn = connect_to_user_db()
    c = conn.cursor()

    c.execute("""CREATE TABLE if not exists AnswerTable(
                CustomAnswerID INTEGER PRIMARY KEY NOT NULL,
                Question TEXT NOT NULL,
                Answer TEXT,
                AnswerType TEXT, 
                AbsoluteTime REAL,
                RelativeTime REAL, 
                ScoreID INTEGER NOT NULL,
                FOREIGN KEY(ScoreID) REFERENCES ScoreTable(CustomScoreID)
                )""")

    conn.commit()
    conn.close()


# --------------------------------------------------------------------------------------------------   Insert Functions:
def insert_into_answer_table(question, answer, answer_type, absolute_time, relative_time, score_id):
    if isinstance(score_id, int):
        conn = connect_to_user_db()
        c = conn.cursor()

        c.execute("""INSERT INTO AnswerTable(
                    Question,
                    Answer,
                    AnswerType, 
                    AbsoluteTime,
                    RelativeTime,
                    ScoreID) VALUES (?, ?, ?, ?, ?, ?)""", (question,
                                                            answer,
                                                            answer_type,
                                                            absolute_time,
                                                            relative_time,
                                                            score_id))
        conn.commit()
        conn.close()
        return answer_type
    else:
        return


# Insert values into table
def insert_into_user_table(firstname, surname, age, profession, nationality):
    conn = connect_to_user_db()
    c = conn.cursor()

    c.execute("""INSERT INTO UserTable (
                Firstname, 
                Surname, 
                Age, 
                Profession, 
                Nationality) VALUES (?, ?, ?, ?, ?)""", (firstname, surname, age, profession, nationality))
    conn.commit()
    conn.close()


def insert_into_score_table(test_form, date, user_id):
    if isinstance(user_id, int):
        conn = connect_to_user_db()
        c = conn.cursor()

        c.execute("""INSERT INTO ScoreTable (TestForm, Date, UserID) VALUES (?, ?, ?)""", (test_form, date, user_id))
        conn.commit()
        conn.close()
        return c.lastrowid
    else:
        return


def update_answer(question, answer, answer_type, absolute_time, relative_time, answer_id):
    if isinstance(answer_id, int):
        conn = connect_to_user_db()
        c = conn.cursor()

        c.execute("""UPDATE AnswerTable SET question = ?,
                  Answer = ?,
                  AnswerType = ?,
                  AbsoluteTime = ?,
                  RelativeTime = ? WHERE rowid= ? """, (
            question,
            answer,
            answer_type,
            absolute_time,
            relative_time,
            answer_id)
                  )
        conn.commit()
        conn.close()
        return answer_type
    else:
        return


# --------------------------------------------------------------------------------------------------   Select Functions:
# Select all from the User Table
def select_all_users():
    conn = connect_to_user_db()
    c = conn.cursor()

    c.execute("SELECT rowid, * FROM UserTable")
    users = c.fetchall()
    conn.commit()
    conn.close()
    return users


# Select current user from User Table

def select_current_user(user_id):
    conn = connect_to_user_db()
    c = conn.cursor()

    c.execute("SELECT rowid, * FROM UserTable WHERE rowid=?", (user_id,))
    current_user = c.fetchone()
    conn.commit()
    conn.close()
    return current_user


# Select score of current user
def select_every_score_for_current_user(user_id):
    conn = connect_to_user_db()
    c = conn.cursor()

    c.execute("SELECT rowid, * FROM ScoreTable WHERE UserID=?", (user_id,))
    current_user_score = c.fetchall()
    conn.commit()
    conn.close()
    return current_user_score


def select_current_score(score_id):
    conn = connect_to_user_db()
    c = conn.cursor()

    c.execute("SELECT rowid, * FROM ScoreTable WHERE CustomScoreID=?", (score_id,))
    selected_score = c.fetchone()
    conn.commit()
    conn.close()
    return selected_score


# Select all answers of current score
def select_every_answer_for_current_score(score_id):
    conn = connect_to_user_db()
    c = conn.cursor()

    c.execute("SELECT rowid, * FROM AnswerTable WHERE ScoreID=?", (score_id,))
    current_user_score = c.fetchall()
    conn.commit()
    conn.close()
    return current_user_score


# Select all reactions of current score
def select_every_reaction_for_current_score(score_id):
    conn = connect_to_user_db()
    c = conn.cursor()

    c.execute("""
    SELECT rowid, * FROM AnswerTable WHERE ScoreID=? AND NOT AnswerType = "Missed" """, (score_id,))
    current_reactions = c.fetchall()
    conn.commit()
    conn.close()
    return current_reactions


def select_specific_answers(score_id, answer_type):
    conn = connect_to_user_db()
    c = conn.cursor()

    c.execute("SELECT * FROM AnswerTable WHERE ScoreID=? AND AnswerType = ?", (score_id, answer_type))
    selected_answers = c.fetchall()
    conn.commit()
    conn.close()
    return selected_answers


'''
# Select every score in the database
def select_every_score():

    connect_to_user_db()
    c.execute("SELECT rowid, * FROM ScoreTable")
    scores = c.fetchall()
    conn.commit()
    conn.close()
    return scores
'''


# --------------------------------------------------------------------------------------------------   Delete Functions:
# Delete selected user from User Table
def delete_user(user_id, score_id):
    conn = connect_to_user_db()
    c = conn.cursor()

    c.execute("DELETE FROM UserTable WHERE rowid=?", (user_id,))
    c.execute("DELETE FROM ScoreTable WHERE UserID=?", (user_id,))
    c.execute("DELETE FROM AnswerTable WHERE ScoreId=?", (score_id,))
    conn.commit()
    conn.close()


# Delete selected user from User Table
def delete_score(score_id):
    conn = connect_to_user_db()
    c = conn.cursor()

    c.execute("DELETE FROM ScoreTable WHERE rowid=?", (score_id,))
    c.execute("DELETE FROM AnswerTable WHERE ScoreId=?", (score_id,))
    conn.commit()
    conn.close()


def delete_answer(score_id):
    conn = connect_to_user_db()
    c = conn.cursor()

    c.execute("DELETE FROM AnswerTable WHERE ScoreId=?", (score_id,))
    conn.commit()
    conn.close()


# --------------------------------------------------------------------------------------   Calculate measured variables:
# Calculate the number of all stimuli
def number_of_stimuli(score_id):
    conn = connect_to_user_db()
    c = conn.cursor()

    c.execute("""SELECT COUNT(*) FROM AnswerTable WHERE ScoreID = ? """, (score_id,))
    num_of_stimuli = c.fetchone()[0]
    conn.commit()
    conn.close()
    return num_of_stimuli


# Calculate the number of all reactions
def number_of_reactions(score_id):
    conn = connect_to_user_db()
    c = conn.cursor()

    c.execute(
        """SELECT COUNT(*) FROM AnswerTable WHERE ScoreID = ? AND NOT AnswerType = "Missed" """,
        (score_id,)
    )
    num_of_stimuli = c.fetchone()[0]
    conn.commit()
    conn.close()
    return num_of_stimuli


# Calculate the number of all chosen answers
def number_of_answers(score_id, answer_type):
    conn = connect_to_user_db()
    c = conn.cursor()

    c.execute(
        """SELECT COUNT(*) FROM AnswerTable WHERE ScoreID = ? AND AnswerType = ? """,
        (score_id, answer_type)
    )
    num_of_answers = c.fetchone()[0]
    conn.commit()
    conn.close()
    return num_of_answers


connect_to_user_db()
