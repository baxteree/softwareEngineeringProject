import sqlite3 as sql

# Returns the planner data from the database using a given ID
def retrieve_planner_data(id):
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()
    data = cur.execute(f"SELECT * FROM planner WHERE id = {id}").fetchall()
    con.close()

    return data

# Inserts new planner data if it does not exist, or replaces it if it does
def insert_planner_data(id, start_date, num_weeks):
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()
    cur.execute("INSERT OR REPLACE INTO planner (id, start_date, weeks) VALUES (?, ?, ?)", (id, start_date, num_weeks))
    con.commit()
    con.close()

