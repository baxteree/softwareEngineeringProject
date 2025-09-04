import sqlite3 as sql
import html
from bcrypt import gensalt
from password_hashing import hashPass
from time import sleep
from random import randint, choices
from string import ascii_letters, digits

# Inserts new user data
def insert_user_data(username, password):
    # Connect to the database and establish a cursor
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()

    # Generate a unique invite code
    while True:
        invite_code = generate_invite_code()
        cur.execute("SELECT 1 FROM users WHERE invite_code = ?", (invite_code,))
        if not cur.fetchone():
            break

    # Make the inputs safe
    safe_user = make_web_safe(username)
    safe_pass = make_web_safe(password)

    # Generate a salt to go with the user
    salt = gensalt()

    hashedpw = hashPass(safe_user, safe_pass, salt)

    # Insert the users details into the database
    cur.execute(
        "INSERT OR IGNORE INTO users (username,password,salt,invite_code) VALUES (?,?,?,?)",
        (
            safe_user,
            hashedpw,
            salt,
            invite_code,
        ),
    )

    # Commit the changes and close the connection
    con.commit()
    con.close()

# Retrieves user data, returns True if the user exists and the password is correct
def retrieve_user_data(username, password):
    # Establish a connection to the database
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()

    # Make the inputs safe
    safe_user = make_web_safe(username)
    safe_pass = make_web_safe(password)

    # Select the user with the specified username
    user = cur.execute("SELECT * FROM users WHERE username = (?)", (safe_user,)).fetchall()

    # If the specified username is not in the database
    if user is None:
        # Return false and close the connection to the database
        con.close()
        return False

    # If this point is reached, the user exists
    else:
        hashedpw = hashPass(safe_user, safe_pass, None)
        user_id = cur.execute("SELECT user_id FROM users WHERE password = (?) AND username = (?) LIMIT 1", (hashedpw, safe_user,)).fetchall()
        user_id = user_id[0][0] if user_id else None

        # Simulate response time of heavy app for security
        sleep(randint(80, 90) / 1000)

        if user_id is None:
            con.close()
            return False
        else:
            con.close()
            return user_id


# Inserts new planner data if it does not exist
def insert_planner_data(planner_name, user_id):
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()

    # Sanitise inputs
    safe_name = make_web_safe(planner_name)

    # Check if the planner already exists
    planners = cur.execute("SELECT planner_name FROM planner WHERE planner_name = (?)", (safe_name,)).fetchall()
    if planners:
        con.close()
        return

    cur.execute("INSERT INTO planner (planner_name, planner_start_date, planner_weeks) VALUES (?, ?, ?)", 
                (safe_name, None, None))
    cur.execute("INSERT INTO plannerMap (user_id, planner_id) VALUES (?, ?)", 
                (user_id, cur.lastrowid))
    con.commit()
    con.close()

# Updates planner data
def update_planner_data(planner_id, planner_name, start_date, num_weeks):
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()

    cur.execute("REPLACE INTO planner (planner_id, planner_name, planner_weeks, planner_start_date) VALUES (?, ?, ?, ?)", 
                (planner_id, planner_name, num_weeks, start_date))
    con.commit()
    con.close()

# Returns the planner data from the database using a given ID
def retrieve_planner_data(planner_id):
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()
    data = cur.execute("SELECT * FROM planner WHERE planner_id = (?)", (planner_id,)).fetchall()
    con.close()

    return data

# Inserts a new task into the database
def insert_task_data(planner_id, name, description, due_date):
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()

    # Sanitise inputs
    safe_name = make_web_safe(name)
    safe_description = make_web_safe(description)

    cur.execute("INSERT INTO tasks (task_planner_id, task_name, task_description, task_due_date) VALUES (?, ?, ?, ?)", (planner_id, safe_name, safe_description, due_date))
    con.commit()
    con.close()

# Returns the planner data from the database using a given ID
def retrieve_task_data(planner_id):
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()
    data = cur.execute("SELECT * FROM tasks WHERE task_planner_id = (?)", (planner_id,)).fetchall()
    con.close()

    return data

# Returns the planner data from the database using a given ID
def retrieve_planners(user_id):
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()
    data = cur.execute("SELECT planner.planner_id, planner.planner_name FROM planner JOIN plannerMap ON plannerMap.planner_id = planner.planner_id WHERE user_id = (?)", (user_id,)).fetchall()
    con.close()

    return data

# Returns just the planner ID from the database using a given user ID
def get_planner_ids(user_id):
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()
    data = cur.execute("SELECT planner_id FROM plannerMap WHERE user_id = (?)", (user_id,)).fetchall()
    con.close()

    data = [item[0] for item in data]

    return data

def invite_user(invite_code, planner_id):
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()

    user_id = cur.execute("SELECT user_id FROM users WHERE invite_code = (?)", (invite_code,)).fetchall()
    user_id = user_id[0][0] if user_id else None

    if not user_id:
        con.close()
        return False
    
    cur.execute("INSERT INTO plannerMap (user_id, planner_id) VALUES (?, ?)", (user_id, planner_id))
    con.commit()
    con.close()
    return True

def get_users(planner_id):
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()

    if not planner_id:
        con.close()
        return []

    users = cur.execute("SELECT users.username FROM users JOIN plannerMap ON plannerMap.user_id = users.user_id WHERE plannerMap.planner_id = (?)", (planner_id,)).fetchall()
    con.close()

    users = [user[0] for user in users]

    return users

def get_invite_code(user_id):
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()

    invite_code = cur.execute("SELECT invite_code FROM users WHERE user_id = (?)", (user_id,)).fetchall()
    con.close()

    invite_code = invite_code[0][0] if invite_code else None

    if invite_code:
        return invite_code
    else:
        return None

# Function to sanitise text using the html library
def make_web_safe(string: str) -> str:
    return html.escape(string)

def generate_invite_code():
    length = 8
    invite_code = ''.join(choices(ascii_letters + digits, k=length))
    return invite_code

