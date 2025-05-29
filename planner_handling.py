from datetime import datetime, timedelta


class Planner:
    def __init__(self, start_date, num_weeks):
        self.start_date = start_date
        self.num_weeks = num_weeks

    # Function that creates a list of weeks, given the start date and the number of weeks
    def create_weeks(self):
        # Parse input date string (format: yyyy-mm-dd)
        start_date = datetime.strptime(self.start_date, "%Y-%m-%d")

        week_dates = []
        # Generate a list of dates for each week starting from the start_date
        for i in range(self.num_weeks):
            week_date = start_date + timedelta(weeks=i)
            week_date = week_date.strftime("%d %B %Y")
            week_dates.append(f"Week {i+1}: {week_date}")
        
        return week_dates


class Task:
    def __init__(self, title, description, due_date, task_type='general'):
        self.title = title
        self.description = description
        self.due_date = due_date
        self.task_type = task_type  # 'general', 'week', or 'out_of_range'