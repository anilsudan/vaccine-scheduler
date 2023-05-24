from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime
from operator import itemgetter


'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None

current_caregiver = None

DATE_FORMAT = '%Y-%m-%d'


def uname_exists(username: str, table: str) -> bool:
    """
    Checks if a given username exists in the database, for either Patients or Caregivers.
    Will error if given an incorrect name.
    @param username: str, username to check
    @param table: str, either 'Patients' or 'Caregivers'
    @return: bool, true if the username exists and false if it does not.
    """
    # check for valid table input
    if table != 'Caregivers' and table != 'Patients':
        raise Exception('Bad table input -- you should not see this :)')
    cm = ConnectionManager()
    conn = cm.create_connection()
    select_username = f"SELECT * FROM {table} WHERE Username = '{username}'"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False


def create_caregiver(tokens: list) -> None:
    """
    Creates caregiver in DB given user input.
    @param tokens: list, contains user input, valid format ['create_caregiver', 'username', 'password']
    @return: None, prints status in console and commits valid info to DB
    """
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return
    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if uname_exists(username, 'Caregivers'):
        print(f'Username taken, try again!')
        return
    salt = Util.generate_salt()
    uhash = Util.generate_hash(password, salt)
    # create the caregiver
    caregiver = Caregiver(username, salt=salt, uhash=uhash)
    # save to caregiver information to our database
    try:
        caregiver.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)


def create_patient(tokens: list) -> None:
    """
    Creates patient in DB given user input.
    @param tokens: list, contains user input, only valid format ['create_patient', 'username', 'password']
    @return: None, prints status in console and commits valid info to DB.
    """
    # Ensure valid input
    if len(tokens) != 3:
        print(f'Error: Failed to create user (username and password required)')
        return None
    uname = tokens[1]
    pw = tokens[2]
    # Ensure username does not already exist.
    if uname_exists(uname, 'Patients'):
        print('Username taken, try again!')
        return
    salt = Util.generate_salt()
    uhash = Util.generate_hash(pw, salt)
    patient = Patient(uname, salt=salt, uhash=uhash)
    try:
        patient.save_to_db()
    except pymssql.Error as e:
        print(f'Failed to create user.')
        print(f'Db-Error: {e}')
        return
    except Exception as e:
        print(f'Failed to create user.')
        print(f'Exception: {e}')
        return
    print(f'Created user {uname}')


def login_patient(tokens: list) -> None:
    """
    Logs in patient given user input.  Requires valid username-password combination.
    @param tokens: list, contains user input, only valid format ['login_patient', 'username', 'password']
    @return: None, prints status in console and sets current logged in patient.
    """
    global current_patient
    if current_caregiver is not None or current_patient is not None:
        print('User already logged in.')
        return
    if len(tokens) != 3:
        print('Login failed.')
        return
    uname = tokens[1]
    pw = tokens[2]
    patient = None
    try:
        patient = Patient(uname, password=pw).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return
    if patient is None:
        print("Login failed.")
    else:
        print(f'Logged in as {uname}')
        current_patient = patient


def login_caregiver(tokens: list) -> None:
    """
    Logs in caregiver given user input.  Requires valid username-password combination.
    @param tokens: list, contains user input, only valid format ['login_patient', 'username', 'password']
    @return: None, prints status in console and sets current logged in caregiver.
    """
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if caregiver is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_caregiver = caregiver


def search_caregiver_schedule(tokens) -> None:
    """
    Searches for available reservations for a given date, printing out the date and the number of Vaccines available.
    @param tokens: list contains user input.  Must be form 'search_caregiver_schedule YYYY-MM-DD
    @return: None, prints status to console.
    """
    global current_caregiver
    global current_patient
    global DATE_FORMAT
    # Ensure someone logs in.
    if current_caregiver is None and current_patient is None:
        print('Error: Please login first!')
        return
    # Ensure date was provided
    if len(tokens) != 2:
        print('Error: Please provide date!')
        return
    # Format date nicely
    try:
        date = datetime.datetime.strptime(tokens[1], DATE_FORMAT)
    except ValueError as e:
        print(f'Error: Could not read date')
        print(f'Datetime Error - {e}')
        return
    # Grab available vaccines and caregivers
    try:
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)
        grab_vaccines = 'SELECT Name, Doses FROM Vaccines;'
        cursor.execute(grab_vaccines)
        vaccines = []
        for row in cursor:
            vaccines.append(f'{row["Name"]} {row["Doses"]}')
        grab_caregivers = 'SELECT AV.AppointmentID, AV.CaregiverID ' \
                          'FROM Availabilities AV LEFT JOIN Appointments AP ' \
                          'ON AP.AppointmentID = AV.AppointmentID ' \
                          'WHERE AP.AppointmentID is null AND AV.Date = %s'
        try:
            slots = []
            cursor.execute(grab_caregivers, str(date.date()))
            for row in cursor:
                slots.append(f'{row["AppointmentID"]} {row["CaregiverID"]}')
            if len(slots) == 0:
                print(f'Sorry, no appointments available for {date}')
                cm.close_connection()
                return
            else:
                print('Currently available reservations:')
                for row in slots:
                    print(row)
                print('Current Vaccine Availability')
                # Print out current amounts of vaccines
                for row in vaccines:
                    print(row)
                cm.close_connection()
                return
        except pymssql.Error as e:
            print('Error: Could not grab caregiver availability')
            print(f'Db-Msg:{e}')
            return
        except Exception as e:
            print(f'Error: {e}')
    except pymssql.Error as e:
        print('Error: Could not connect to DB and/or grab vaccine info.')
        print(f'DB-Msg: {e}')
        return
    except Exception as e:
        print(f'Error: {e}')
        return
    finally:
        cm.close_connection()


def reserve(tokens):
    """
    """
    # Check if user is logged in as patient
    global current_patient, current_caregiver
    if current_patient is None and current_caregiver is None:
        print('Error: Please login first.')
        return
    elif current_patient is None:
        print('Error: Please login as a patient.')
        return

    # Ensure valid input
    if len(tokens) != 3:
        print(f'Error: Please provide valid date {DATE_FORMAT} and vaccine information.')
        return
    # Ensure valid date
    try:
        date = datetime.datetime.strptime(tokens[1], DATE_FORMAT)
    except ValueError as e:
        print(f'Error: Could not read date')
        print(f'Datetime Error - {e}')
        return
    vac_name = tokens[2]

    # Queries used :)
    check_vaccine_amt = 'SELECT Doses FROM Vaccines V WHERE V.Name = %s'
    grab_caregivers = 'SELECT AV.AppointmentID, AV.CaregiverID ' \
                      'FROM Availabilities AV LEFT JOIN Appointments AP ' \
                      'ON AP.AppointmentID = AV.AppointmentID ' \
                      'WHERE AP.AppointmentID is null AND AV.Date = %s'
    add_apt = 'INSERT INTO Appointments VALUES (%s, %s, %s)'

    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)
    # Check to ensure that there is enough of the specified vaccine in reserve.
    try:
        cursor.execute(check_vaccine_amt, vac_name)
        for row in cursor:
            dose_amt = row['Doses']
    except pymssql.Error as e:
        print('Error: Could not check Vaccine dose amount')
        print(f'Db-Msg: {e}')
        return
    except Exception as e:
        print(f'Error: {e}')
        return
    if dose_amt < 1:
        print(f'Sorry, there are not enough doses of {vac_name} vaccine.')
        return

    # Check for open appointments on this date.
    apps = []
    try:
        cursor.execute(grab_caregivers, date)
        for row in cursor:
            apps.append([row['AppointmentID'], row['CaregiverID']])
    except pymssql.Error as e:
        print('Error: Could not check Vaccine dose amount')
        print(f'Db-Msg: {e}')
        return
    except Exception as e:
        print(f'Error: {e}')
        return
    if len(apps) < 1:
        print(f'Sorry, there are no open appointments on {date}.')
        return

    # Choose the appointment based on the person's name, sorted alphabetically
    apps = sorted(apps, key=itemgetter(1))
    apt = apps[0]

    # Decrease vaccine amount
    try:
        vac = Vaccine(vac_name, dose_amt)
        vac.decrease_available_doses(1)
    except pymssql.Error as e:
        print('Error: Could not update vaccine count.')
        print(f'Db-Msg: {e}')
        return
    except Exception as e:
        print(f'Error: {e}')
        return

    # Add this appointment to the table
    try:
        cursor.execute(add_apt, (apt[0], vac_name, current_patient.get_username()))
        conn.commit()
    except pymssql.Error as e:
        vac.increase_available_doses(1)  # RESET VACCINE DOSES
        print('Error: Could not add appointment.')
        print(f'Db-Msg: {e}')
        return
    except Exception as e:
        vac.increase_available_doses(1)  # RESET VACCINE DOSES
        print(f'Error: {e}')
        return

    # If this executes, then everything has been updated correctly
    print('Vaccine appointment scheduled!')
    print(f'Appointment ID: {apt[0]}, Caregiver: {apt[1]}')
    cm.close_connection()
    return


def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver, DATE_FORMAT
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    try:
        d = datetime.datetime.strptime(tokens[1], DATE_FORMAT)
        current_caregiver.upload_availability(d)
    except pymssql.Error as e:
        print("Upload Availability Failed")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print(f"Error: Please enter a valid date in format {DATE_FORMAT}")
        return
    except Exception as e:
        print("Error occurred when uploading availability")
        print("Error:", e)
        return
    print("Availability uploaded!")


def cancel(tokens):
    """
    """
    global current_caregiver, current_patient
    # Ensure a user is logged in
    if current_caregiver is None and current_patient is None:
        print('Error: Please login first!')
        return
    # Ensure an ID was provided
    if len(tokens) != 2:
        print('Error: Please provide an AppointmentID to cancel.')
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)
    vac_query = 'SELECT AP.VaccineType FROM Appointments AP WHERE AP.AppointmentID = %s'
    del_query = 'DELETE FROM Appointments WHERE AppointmentID = %s'
    # If currently logged in as patient
    if current_caregiver is None:
        query = 'SELECT AP.PatientID FROM Appointments AP WHERE AP.AppointmentID = %s'
        try:
            cursor.execute(query, tokens[1])
            id_from_db = None
            for row in cursor:
                id_from_db = row['PatientID']
            if id_from_db is None:
                print('Error: Appointment not found.')
            elif id_from_db != current_patient.get_username():
                print('Error: This appointment is not registered under your user account.')
                return
            else:
                try:
                    cursor.execute(vac_query, tokens[1])
                    for row in cursor:
                        vac_name = str(row['VaccineType'])
                    vac = Vaccine(vac_name, 'DUMMY').get()
                    vac.increase_available_doses(1)
                    cursor.execute(del_query, tokens[1])
                    conn.commit()
                    print('Appointment successfully cancelled!')
                except pymssql.Error as e:
                    print('Error: Could not cancel appointment.')
                    print(f'Db-Msg: {e}')
                except Exception as e:
                    print('Error: Please try again!')
                    print(e)
        except pymssql.Error as e:
            print('Error: Could not lookup appointment.')
            print(f'Db-Msg: {e}')
        except Exception as e:
            print('Error: Please try again!')
            print(e)
        finally:
            cm.close_connection()
            return
    # If currently logged in as caregiver
    elif current_patient is None:
        query = 'SELECT AV.CaregiverID FROM Availabilities AV, Appointments AP ' \
                'WHERE AV.AppointmentID = AP.AppointmentID AND AV.AppointmentID = %s'
        try:
            cursor.execute(query, tokens[1])
            id_from_db = None
            for row in cursor:
                id_from_db = row['CaregiverID']
            if id_from_db is None:
                print('Error: Appointment not Found')
            elif id_from_db != current_caregiver.get_username():
                print('Error: This appointment is not registered under your user account.')
            else:
                try:
                    cursor.execute(vac_query, tokens[1])
                    for row in cursor:
                        vac_name = row['VaccineType']
                    vac = Vaccine(vac_name, 'DUMMY').get()
                    vac.increase_available_doses(1)
                    cursor.execute(del_query, tokens[1])
                    conn.commit()
                    print('Appointment successfully cancelled!')
                    print('Note: This date will be marked as available and be reservable by other patients.')
                except pymssql.Error as e:
                    print('Error: Could not cancel appointment.')
                    print(f'Db-Msg: {e}')
                except Exception as e:
                    print('Error: Please try again!')
                    print(e)
        except pymssql.Error as e:
            print('Error: Could not lookup appointment.')
            print(f'Db-Msg: {e}')
        except Exception as e:
            print('Error: Please try again!')
            print(e)
        finally:
            cm.close_connection()
            return


def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    vaccine_name = tokens[1]
    doses = int(tokens[2])
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error as e:
        print("Error occurred when adding doses")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when adding doses")
        print("Error:", e)
        return

    # if the vaccine is not found in the database, add a new (vaccine, doses) entry.
    # else, update the existing entry by adding the new doses
    if vaccine is None:
        vaccine = Vaccine(vaccine_name, doses)
        try:
            vaccine.save_to_db()
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    print("Doses updated!")


def show_appointments(tokens):
    """
    """
    global current_caregiver, current_patient
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)
    # if user is not logged in
    if current_caregiver is None and current_patient is None:
        print('Error: Please login first.')
    # If user is a patient
    elif current_caregiver is None:
        user = current_patient.get_username() # noqa
        grab_patient_apts = 'SELECT AP.AppointmentID, AP.VaccineType, AV.Date, AV.CaregiverID ' \
                            'FROM Appointments AP, Availabilities AV ' \
                            'WHERE AP.AppointmentId = AV.AppointmentId AND AP.PatientID = %s ' \
                            'ORDER BY AppointmentID'
        try:
            cursor.execute(grab_patient_apts, user)
            apts = []
            for row in cursor:
                apts.append([row['AppointmentID'], row['VaccineType'], row['Date'], row['CaregiverID']])
            cm.close_connection()
            if len(apts) == 0:
                print(f'No current appointments are scheduled for {user}')
                return
            else:
                print(f'Current appointments scheduled for {user}')
                for apt in apts:
                    print(f'{apt[0]} {apt[1]} {apt[2]} {apt[3]}')
                return
        except pymssql.Error as e:
            print('Error: Could not lookup appointments.')
            print(f'Db-Msg: {e}')
            return
        except Exception as e:
            print('Please try again!')
            print(f'Error: {e}')
            return
    # If user is a caregiver
    elif current_patient is None:
        user = current_caregiver.get_username()
        grab_patient_apts = 'SELECT AP.AppointmentID, AP.VaccineType, AV.Date, AP.PatientID ' \
                            'FROM Appointments AP, Availabilities AV ' \
                            'WHERE AP.AppointmentId = AV.AppointmentId AND AV.CaregiverID = %s ' \
                            'ORDER BY AppointmentID'
        try:
            cursor.execute(grab_patient_apts, user)
            apts = []
            for row in cursor:
                apts.append([row['AppointmentID'], row['VaccineType'], row['Date'], row['PatientID']])
            cm.close_connection()
            if len(apts) == 0:
                print(f'No current appointments are scheduled for {user}')
                return
            else:
                print(f'Current appointments scheduled for {user}')
                for apt in apts:
                    print(f'{apt[0]} {apt[1]} {apt[2]} {apt[3]}')
                return
        except pymssql.Error as e:
            print('Error: Could not lookup appointments.')
            print(f'Db-Msg: {e}')
            return
        except Exception as e:
            print(f'Please try again! {e}')
            return


def logout(tokens):
    """
    """
    global current_caregiver, current_patient
    if current_caregiver is None and current_patient is None:
        print('Error: Log in first.')
        return
    else:
        current_caregiver = None
        current_patient = None
        print('Successfully logged out!')
        return


def start():
    stop = False
    print()
    print(" *** Please enter one of the following commands *** ")
    print("> create_patient <username> <password>")  # //TODO: implement create_patient (Part 1)
    print("> create_caregiver <username> <password>")
    print("> login_patient <username> <password>")  # // TODO: implement login_patient (Part 1)
    print("> login_caregiver <username> <password>")
    print("> search_caregiver_schedule <date>")  # // TODO: implement search_caregiver_schedule (Part 2)
    print("> reserve <date> <vaccine>")  # // TODO: implement reserve (Part 2)
    print("> upload_availability <date>")
    print("> cancel <appointment_id>")  # // TODO: implement cancel (extra credit)
    print("> add_doses <vaccine> <number>")
    print("> show_appointments")  # // TODO: implement show_appointments (Part 2)
    print("> logout")  # // TODO: implement logout (Part 2)
    print("> Quit")
    print()
    while not stop:
        response = ""
        print("> ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Please try again!")
            break

        response = response.lower()
        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Please try again!")
            continue
        operation = tokens[0]
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == cancel:
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "cancel":
            cancel(tokens)
        elif operation == "quit":
            print("Bye!")
            stop = True
        else:
            print("Invalid operation name!")


if __name__ == "__main__":
    '''
    // pre-define the three types of authorized vaccines
    // note: it's a poor practice to hard-code these values, but we will do this ]
    // for the simplicity of this assignment
    // and then construct a map of vaccineName -> vaccineObject
    '''

    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()
