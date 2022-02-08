import sqlite3
import os
import numpy.random as random

# Sets Database Name

database_file = "school.db"

# Tells the program if it should
# delete the database if it fails
# to set up.

database_remove_on_failure = True

# Checks if the file exists

setup = os.path.exists(database_file)

# Initialises the variable

con = None

# Sets debug mode to false
# will avoid showing any errors
# that might occur when running
# the program.

program_debug = False

try:
    # Connects to the database
    con = sqlite3.connect(database_file)
except Exception as error:
    if program_debug:
        print(error)


def setup_database(force=False):
    global con

    # Sets up the database by
    # adding the tables that will
    # be needed in the database
    # for the program to successfully
    # run.

    if force:
        # Force will remove the database
        # and make sure that the program
        # creates a clean version of the
        # database which might be handy
        # for the teacher or program.

        if os.path.exists(database_file):
            if con:
                con.close()
            os.remove(database_file)
        try:
            con = sqlite3.connect(database_file)
        except Exception as err:
            if program_debug:
                print(err)

    try:

        con.execute('''
            CREATE TABLE students(
                ID INTEGER PRIMARY KEY NOT NULL, 
                first_name TEXT(30) NOT NULL,
                last_name TEXT(30) NOT NULL,
                class_name TEXT NOT NULL
            )
        ''')

        con.execute('''
            CREATE TABLE arithmetic_test(
                ID INTEGER PRIMARY KEY NOT NULL,
                student_ID INTEGER NOT NULL,
                score_1 REAL NOT NULL,
                score_2 REAL NOT NULL,
                score_3 REAL NOT NULL,
                average_score REAL NOT NULL
            )
        ''')

        # Saves the database

        con.commit()

    except Exception as err:
        if con:
            con.close()
        if database_remove_on_failure:
            os.remove(database_file)
        raise SystemError(f"Failed to setup database file with error: {err}")


if not setup:
    setup_database()


def get_test_id():
    # Sets Min
    largest_id = 100000
    try:
        # Gets ID from table
        for row in con.execute("SELECT ID FROM arithmetic_test"):
            if row[0] > largest_id:
                largest_id = row[0]  # Sets largest ids
        # Increments
        return largest_id + 1
    except Exception as err:
        print(f"Failed to get test id with error: {err}")


def get_student_id():
    # Sets Min
    largest_id = 100000
    try:
        # Gets ID from table
        for row in con.execute("SELECT ID FROM students"):
            if row[0] > largest_id:
                # Sets largest ids
                largest_id = row[0]
        # Increments
        return largest_id + 1
    except Exception as err:
        if program_debug:
            print(err)


def average_score(scores=None):
    if not scores:
        return 0
    else:
        length = len(scores)
        total = 0
        for score in scores:
            total += score
        average = total / length
        return average


def submit_arithmetic_results(sid=0, score_1=0, score_2=0, score_3=0):
    try:
        # Inserts the data into the table and commits it.
        con.execute('''
            INSERT INTO arithmetic_test(ID, student_ID, score_1, score_2, score_3, average_score)
            VALUES(?,?,?,?,?,?)
        ''', (get_test_id(), sid, score_1, score_2, score_3, average_score([score_1, score_2, score_3])))
        con.commit()
        return True
    except Exception as err:
        if program_debug:
            print(err)

        return False


def user_exists(sid=0):
    for row in con.execute(f"SELECT ID FROM students WHERE ID={sid}"):
        if row:
            return True
    return False


def get_score(calculation="", answer=0):
    # Holds the user in the loop
    while True:
        try:
            user_answer = float(input(calculation))
            answer = round(answer, 2)
            user_answer = round(user_answer, 2)
            user_answer = int(user_answer)
            answer = int(answer)

            if user_answer is not answer:
                print(f"\nIncorrect Answer. 0 Points awarded. The answer was {answer}")
                return 0
            else:
                print("\nCorrect Answer. 1 Point has been awarded.")
                return 1
        except Exception as err:
            if program_debug:
                print(err)


def test_user(min_num=0, max_num=10, questions=10, student_id=0):
    # This function uses numpy to be
    # able to generate random numbers
    # between the min_num and max_num
    # the program also uses a random
    # number from 0 to 4 which decides
    # the sign that will be used,
    # the program will check if the user
    # is correct it will give the user
    # a point if not it will not give
    # the user a point.

    scores = []
    count = 0
    # Holds the user in the loop
    while True:
        count += 1
        try:
            question_scores = []
            for question_num in range(0, questions):
                num_1 = random.randint(min_num, max_num)
                num_2 = random.randint(min_num, max_num)
                sign = random.randint(0, 4)
                answer = 0
                if sign == 0:
                    sign = "+"
                    answer = num_1 + num_2
                elif sign == 1:
                    sign = "-"
                    answer = num_1 - num_2
                elif sign == 2:
                    sign = "/"
                    answer = num_1 / num_2
                elif sign == 3:
                    sign = "*"
                    answer = num_1 * num_2

                question_scores.append(get_score(f"\n\n(2 Decimal Place): {str(num_1)} {sign} {str(num_2)} = ", answer))
                total = 0
                for s in question_scores:
                    total += s

                scores.append(total)

                if count == 3:
                    break
        except Exception as err:
            if program_debug:
                print(err)

        if count == 3:
            break

    success = submit_arithmetic_results(sid=student_id, score_1=scores[0], score_2=scores[1], score_3=scores[2])

    if success:
        print("\nAdded test scores.\n")
    else:
        print("\nFailed to add test scores.\n")


def create_student():
    # This function gets the user
    # to input information which
    # is validated, once the user
    # has typed out valid data into
    # the program it will save the data
    # into the database which can be
    # accessed at a later date.

    while True:
        try:

            while True:
                first_name = input("\nFirst Name: ")
                if 4 <= len(first_name) <= 30:
                    break
                else:
                    print("\nInvalid response.\n")
            while True:
                last_name = input("Last Name: ")
                if 4 <= len(last_name) <= 30:
                    break
                else:
                    print("\nInvalid response.\n")
            while True:
                class_name = input("Class Name: ")
                if 4 <= len(class_name) <= 30:
                    break
                else:
                    print("\nInvalid response.\n")

            try:
                sid = get_student_id()
                con.execute('''
                    INSERT INTO students(ID, first_name, last_name, class_name)
                    VALUES(?,?,?,?)
                ''', (sid, first_name, last_name, class_name))
                con.commit()
                print(f"\nSuccessfully signed up!\nStudent ID is {str(sid)}")
                break
            except Exception as err:
                if program_debug:
                    print(err)
                print("\nFailed to sign up, please try again.")
        except Exception as err:
            if program_debug:
                print(err)


def submit_grade():
    # This allows the staff
    # to be able to add the students
    # test scores into the system manually
    # though the teacher could allow the
    # student to be able to take the test instead
    # which could save the teachers time.

    # This will take input from the teacher
    # and assign the data in the database once
    # the data has been validated.

    while True:
        try:
            while True:
                try:
                    has_account = input("Does the student have a student ID? (Y/N) ")
                    if has_account.lower() == "n":
                        create_student()
                        break
                    elif has_account.lower() == "y":
                        break
                except Exception as err:
                    if program_debug:
                        print(err)
            student_id = 0

            while True:
                try:
                    student_id = input("Student ID: ")
                    if student_id.lower() == "create":
                        create_student()
                    else:
                        student_id = int(student_id)

                    if user_exists(student_id):
                        break
                    else:
                        print("\nFailed to find user. Type create if you don't have a student ID.")
                except Exception as err:
                    if program_debug:
                        print(err)

            while True:
                try:
                    score_1 = int(input("Score 1: "))
                    if 0 < score_1 < 30:
                        break
                except Exception as err:
                    if program_debug:
                        print(err)

            while True:
                try:
                    score_2 = int(input("Score 2: "))
                    if 0 < score_2 < 30:
                        break
                except Exception as err:
                    if program_debug:
                        print(err)

            while True:
                try:
                    score_3 = int(input("Score 3: "))
                    if 0 < score_2 < 30:
                        break
                except Exception as err:
                    if program_debug:
                        print(err)

                # Adds the information to
                # the database and checks
                # if the system was able
                # to add the data to the
                # database successfully

            success = submit_arithmetic_results(student_id, score_1, score_2, score_3)
            if success:
                print("\nAdded Entry.")

                more = input("\nDo you wish to add more? (Y/N) ")
                if more.lower() == "n":
                    break
            else:
                print("Failed to add Entry.")
        except Exception as err:
            if program_debug:
                print(err)


def wipe_database():
    # Checks if the user is sure
    # that they want to delete the
    # database and then proceeds
    # depending on what the user
    # wants to do.

    while True:
        confirmation = input("\nAre you sure that want to wipe the database? (Y/N) ")
        if confirmation.lower() == "y":
            setup_database(True)
            break
        elif confirmation.lower() == "n":
            break


def display_test_data():
    # This will display information about the user
    # The program will grab the data from the database
    # and will display it in a user-friendly manner.
    # Uses a loop in order to keep the user in the menu.

    while True:
        try:
            display_options = "\nDisplay Options\n"
            display_options = display_options + "\nOption 1: Alphabetically"
            display_options = display_options + "\nOption 2: Score (highest to lowest)"
            display_options = display_options + "\nOption 3: Average Score (highest to lowest)"
            display_options = display_options + "\nOption 4: Show all data"
            display_options = display_options + "\nOption 5: Exit Menu"
            print(display_options)
            display_choice = int(input("\n\nUser Choice: "))

            if display_choice == 1:

                # Selects data from the database
                # and orders it, this then
                # displays the data for the user
                # to view.

                for main_row in con.execute("SELECT class_name, first_name, last_name, MAX(score_1, score_2, score_3) "
                                            "as high_score FROM students, arithmetic_test ORDER BY class_name, "
                                            "first_name, last_name ASC"):
                    print(f"\n{main_row[0]}: {main_row[1]} {main_row[2]} Score: {main_row[3]}")
            elif display_choice == 2:

                # Selects data from the database
                # and orders it, this then
                # displays the data for the user
                # to view.

                for main_row in con.execute("SELECT class_name, first_name, last_name, MAX(score_1, score_2, score_3) "
                                            "as high_score FROM students, arithmetic_test ORDER BY high_score DESC"):
                    print(f"\n{main_row[0]}: {main_row[1]} {main_row[2]} Score: {main_row[3]}")
            elif display_choice == 3:

                # Selects data from the database
                # and orders it, this then
                # displays the data for the user
                # to view.

                for main_row in con.execute("SELECT class_name, first_name, last_name, average_score FROM students, "
                                            "arithmetic_test ORDER BY average_score DESC"):
                    print(f"\n{main_row[0]}: {main_row[1]} {main_row[2]} Score: {main_row[3]}")
            elif display_choice == 4:

                # Selects data from the database then
                # displays the data for the user
                # to view.

                for main_row in con.execute("SELECT * FROM students"):
                    print(f"\n{main_row[0]} {main_row[1]} {main_row[2]} {main_row[3]}")
                    for row in con.execute("SELECT ID, score_1, score_2, score_3, average_score FROM arithmetic_test"):
                        print(
                            f"Test {row[0]}:\nScore 1: {row[1]}\nScore 2: {row[2]}\n"
                            f"Score 3: {row[3]}\nAverage: {row[4]}")
            elif display_choice == 5:
                break

        except Exception as err:
            print(f"Display Error: {err}")


def main_menu():

    # Creates a loop that the user
    # will be stuck in, this will
    # allow the user to be able
    # to choose from the options
    # available to them.

    while True:
        try:
            menu_options = "\nStudent Grader\n"
            menu_options = menu_options + "\nOption 1: Submit Grade"
            menu_options = menu_options + "\nOption 2: Take Test"
            menu_options = menu_options + "\nOption 3: View Test Data"
            menu_options = menu_options + "\nOption 4: System Statistics"
            menu_options = menu_options + "\nOption 5: Wipe Database"
            menu_options = menu_options + "\nOption 6: Exit Program"
            # Show options
            print(menu_options)
            # Gets user input
            menu_choice = int(input("\n\nUser Choice: "))

            if menu_choice == 1:
                submit_grade()
            elif menu_choice == 2:
                while True:
                    try:
                        signed_up = input("Do you have a student ID? (Y/N) ")
                        if signed_up.lower() == "n":
                            # Signs the user up with a student ID
                            create_student()
                        if signed_up.lower() == "n" or "y":
                            # Requests the student ID
                            sid = int(input("Student ID: "))
                            # Checks if valid User
                            if user_exists(sid):
                                # Tests the User
                                test_user(student_id=sid)
                                break
                    except Exception as err:
                        if program_debug:
                            print(err)

            elif menu_choice == 4:
                display_test_data()
            elif menu_choice == 5:
                wipe_database()
            elif menu_choice == 6:
                break

        except Exception as err:
            if program_debug:
                print(err)


# Checks if the file is being
# run directly if so it will
# open the main menu.

if __name__ == "__main__":
    main_menu()

# Checks if the database
# connection exists if it
# does it will close the
# connection.

if con:
    con.close()
