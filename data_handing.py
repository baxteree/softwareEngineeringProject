import sqlite3 as sql

# Inserts new planner data if it does not exist, or replaces it if it does
def insert_planner_data(id, start_date, num_weeks):
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()
    cur.execute("INSERT OR REPLACE INTO planner (planner_id, planner_weeks, planner_start_date) VALUES (?, ?, ?)", (id, num_weeks, start_date))
    con.commit()
    con.close()

# Returns the planner data from the database using a given ID
def retrieve_planner_data(id):
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()
    data = cur.execute(f"SELECT * FROM planner WHERE planner_id = {id}").fetchall()
    con.close()

    return data

# Inserts a new task into the database
def insert_task_data(planner_id, name, description, due_date):
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()
    cur.execute("INSERT INTO tasks (task_planner_id, task_name, task_description, task_due_date) VALUES (?, ?, ?, ?)", (planner_id, name, description, due_date))
    con.commit()
    con.close()

# Returns the planner data from the database using a given ID
def retrieve_task_data(planner_id):
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()
    data = cur.execute(f"SELECT * FROM tasks WHERE task_planner_id = {planner_id}").fetchall()
    con.close()

    return data