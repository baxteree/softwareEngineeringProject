import sqlite3 as sql
import bcrypt as bcrypt

# Retrieve the salt for given a username
def retrieveSalt(username):
    # Connect to the database and establish a cursor
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()

    # Grab the salt from the database
    salt = cur.execute("SELECT salt FROM users WHERE username = (?)", (username,))
    salt = salt.fetchone()

    # Disconnect from the database
    con.close()

    # As the salt is returned as a tuple, get the 'blob' only
    salt = salt[0]

    return salt

# Hash the password, given a username and password
def hashPass(username, password, salt):
    # First salt is dependent on wether one exists for this user or not

    # If the salt isn't provided:
    if salt is None:
        # Get the salt using this function which
        # pulls the salt from the database
        salt1 = retrieveSalt(username)
    else:
        # Otherwise the salt is the one provided
        salt1 = salt

    # Second salt is predetermined
    salt2 = b"$2b$12$sXtl2UlBRwnpIxyoJEPcmu"

    # Encode the password so that python can handle it
    encoded = password.encode()

    # Hash twice, each with the separate salts
    try:
        hashed = bcrypt.hashpw(password=encoded, salt=salt1)
        doubleHashed = bcrypt.hashpw(password=hashed, salt=salt2)
    except TypeError:
        # This general error statement is printed if the salt is invalid
        print("An error occured")
        return None

    return doubleHashed
