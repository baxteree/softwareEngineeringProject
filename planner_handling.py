from datetime import datetime, timedelta
from data_handling import retrieve_planner_data, retrieve_task_data, get_users
from flask import render_template

class Planner:
    def __init__(self, start_date, num_weeks):
        #                          Format correctly
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d")
        self.num_weeks = int(num_weeks)

    # Function that creates a list of weeks, given the start date and the number of weeks
    def create_weeks(self):
        start_date = self.start_date

        week_dates = []
        # Generate a list of dates for each week starting from the start_date
        for i in range(self.num_weeks):
            week_date = start_date + timedelta(weeks=i)
            week_date = week_date.strftime("%d %B %Y")
            week_dates.append(f"{week_date}")

        # Returns a list of dates for each week starting from the start_date
        return week_dates
    
    # Simply returns the start date
    def return_start_date(self):
        return self.start_date
    
    # Simply returns the number of weeks
    def return_weeks(self):
        return self.num_weeks


class Task:
    def __init__(self, title, description, due_date):
        self.title = title
        self.description = description
        #                          Format correctly
        self.due_date = datetime.strptime(due_date, "%Y-%m-%d")
        
    def classify_task(self, start_date, num_weeks):
        # Find the week number for the task based on its due date
        for i in range(num_weeks):
            week_start = start_date + timedelta(weeks=i)
            week_end = week_start + timedelta(weeks=1)
            if week_start <= self.due_date < week_end:
                return i + 1
        return 'general'

    # Creates a task to be handled in the html files
    def create_task(self, start_date, num_weeks):
        title = self.title
        description = self.description
        due_date = self.due_date.strftime("%d %B %Y")
        task_week = self.classify_task(start_date, num_weeks)
        # Returns a list of the task's attributes
        return [title, description, due_date, task_week]

# Makes a list of tasks to be returned to the html file
def make_task_list(task_data, start_date, num_weeks):
    task_list = []
    for task in task_data:
        task_ = Task(task[2], task[3], task[4])
        task_list.append(task_.create_task(start_date, num_weeks))
    return task_list

# Renders the planner page given a chosen planner and the list of planner IDs
def render_planner_page(chosen_planner, chosen_planner_data, users_invite_id):
    planner_data = retrieve_planner_data(chosen_planner)
    users = get_users(chosen_planner)

    if not planner_data:
        return render_template("/planner.html", weeks=None, task_data=None, planners=chosen_planner_data, current_planner=chosen_planner, planner_name=None, users=users, users_invite_id=users_invite_id)
    planner_name = str(planner_data[0][1])
    start_date = planner_data[0][2]
    num_weeks = planner_data[0][3]
    if chosen_planner is False or start_date is None or num_weeks is None:
        return render_template("/planner.html", weeks=None, task_data=None, planners=chosen_planner_data, current_planner=chosen_planner, planner_name=planner_name, users=users, users_invite_id=users_invite_id)
    planner_ = Planner(start_date, num_weeks)
    weeks = planner_.create_weeks()
    task_data = retrieve_task_data(chosen_planner)
    task_list = make_task_list(task_data, planner_.return_start_date(), planner_.return_weeks())
    return render_template("/planner.html", weeks=weeks, task_data=task_list, planners=chosen_planner_data, current_planner=chosen_planner, planner_name=planner_name, users=users, users_invite_id=users_invite_id)
