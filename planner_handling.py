from datetime import datetime, timedelta


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


# Create a test planner
# test = Planner("2023-10-01", 4)

# Print a list of start dates for each week
# print(test.create_weeks())

# Create a test task
# test2 = Task("Test Task", "This is a test task", "2023-11-11")

# Print a list of attributes of the task
# print(test2.create_task(test.return_start_date(), test.return_weeks()))
