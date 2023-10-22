import datetime
import json
import subprocess
import sys
import time
import bisect


class Task:
    days = { # Dictionary to convert day of week to integer
        'monday': 0,
        'tuesday': 1,
        'wednesday': 2,
        'thursday': 3,
        'friday': 4,
        'saturday': 5,
        'sunday': 6
    }

    def __init__(self, command, day_of_week, execution_time, *args):
        self.command = command

        if day_of_week.lower() not in self.days:
            raise ValueError(f"Invalid day of week: {day_of_week}")

        self.day_of_week = day_of_week.lower()
        self.execution_time = execution_time
        self.args = args
        self.next_datetime = self.get_next_datetime()

    def get_next_datetime(self):
        now = datetime.datetime.now()
        next_time = datetime.datetime.strptime(self.execution_time, '%H:%M').time()  # gets only the time part
        day_gap = (self.days[self.day_of_week] - now.weekday()) % 7

        # If it's today but the time has passed, schedule for next week
        if day_gap == 0 and (now.time() >= next_time):
            day_gap = 7

        next_date = now.date() + datetime.timedelta(days=day_gap)
        next_datetime = datetime.datetime.combine(next_date, next_time)

        return next_datetime


class Scheduler:
    def __init__(self):
        self.tasks = []

    def add_task(self, task: Task):
        # bisect insort based on task next_datetime
        bisect.insort(self.tasks, (task.next_datetime, task))

    def wait_for_next_task(self):
        next_task = self.tasks.pop(0)  # force variable to be a task
        # datetime now get microseconds
        print(f"Running Next Task At: {next_task[0]}")
        time.sleep((next_task[1].get_next_datetime() - datetime.datetime.now()).total_seconds())
        # Reschedule task for next week
        next_task[1].next_datetime += datetime.timedelta(days=7)
        self.add_task(next_task[1])
        return next_task[1]


def parse_config(config_file):
    with open(config_file) as f:
        config = json.load(f)

    return config


def schedule_tasks(scheduler, config_dict):
    command = config_dict['command']
    day_of_week = config_dict['day_of_week']
    # latency_period = config_dict['latency_period']

    for task in config_dict['schedule']:
        execution_time = task['time']
        args = task['args']
        t = Task(command, day_of_week, execution_time, *args)
        scheduler.add_task(t)


def run_tasks(scheduler):
    while True:
        task = scheduler.wait_for_next_task()
        subprocess.run([task.command, *task.args])


def main(args):
    config_location = args[0]
    config_dict = parse_config(config_location)  # Parses JSON into a Python dictionary
    scheduler = Scheduler()  # Initializes a scheduler object
    schedule_tasks(scheduler, config_dict)  # Schedules tasks based on the config file
    run_tasks(scheduler)  # Run the tasks that were parsed from the config file -- will run every week forever.


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python scheduler.py <config_file>')
        sys.exit(1)
    elif len(sys.argv) > 2:
        print('Too many arguments!\nUsage: python scheduler.py <config_file>')
        sys.exit(1)

    main(sys.argv[1:])
