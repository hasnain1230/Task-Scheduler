import datetime
import json
import os
import signal
import subprocess
import sys
import time
import bisect

import Constants
import Errors


class Task:
    days = Constants.DAYS_DICT

    def __init__(self, command, day_of_week, execution_time, *args):
        self.command = command

        if day_of_week.lower() not in self.days:
            raise ValueError(Errors.INVALID_DAY_OF_WEEK.format(day_of_week=day_of_week))

        self.day_of_week = day_of_week.lower()
        self.execution_time = execution_time
        self.args = args
        self.next_datetime = self.get_next_datetime()

    def get_next_datetime(self):
        now = datetime.datetime.now()
        next_time = datetime.datetime.strptime(self.execution_time,
                                               Constants.TIME_FORMAT).time()  # gets only the time part
        day_gap = (self.days[self.day_of_week] - now.weekday()) % Constants.TOTAL_DAYS_OF_WEEK

        # If it's today but the time has passed, schedule for next week
        if day_gap == 0 and (now.time() >= next_time):
            day_gap = Constants.TOTAL_DAYS_OF_WEEK

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
        next_task[1].next_datetime += datetime.timedelta(days=Constants.TOTAL_DAYS_OF_WEEK)
        self.add_task(next_task[1])
        return next_task[1]


def parse_config(config_file):
    with open(config_file) as f:
        config = json.load(f)

    return config


def schedule_tasks(scheduler, config_dict):
    command = config_dict[Constants.CONFIG_DICT_COMMAND_KEY]
    day_of_week = config_dict[Constants.CONFIG_DICT_DAY_OF_WEEK_KEY]
    # latency_period = config_dict['latency_period']

    for task in config_dict[Constants.CONFIG_DICT_SCHEDULE_KEY]:
        execution_time = task[Constants.CONFIG_DICT_TIME_KEY]
        args = task[Constants.CONFIG_DICT_ARGS_KEY]
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


def handle_lock_file():
    # If Windows
    if os.name == Constants.WINDOWS_PLATFORM:
        lock_file_path = Constants.LOCK_FILE_PATH_WINDOWS
    # If Linux
    elif os.name == Constants.LINUX_PLATFORM:
        lock_file_path = Constants.LOCK_FILE_PATH_LINUX
    # If Mac
    elif os.name == Constants.MAC_PLATFORM:
        lock_file_path = Constants.LOCK_FILE_PATH_MAC
    else:
        lock_file_path = Constants.LOCK_FILE_GENERIC

    # Check if the lock file exists
    if os.path.exists(lock_file_path):
        # Get the PID of the process that created the lock file
        with open(lock_file_path, 'r') as f:
            pid = f.read()
        return False, pid

    os.makedirs(os.path.dirname(lock_file_path), exist_ok=True)

    with open(lock_file_path, 'w') as f:
        pid = os.getpid()
        f.write(str(pid))

    return True, pid, lock_file_path


def make_signal_handler(lock_file_path):
    def signal_handler(sig, frame):
        os.remove(lock_file_path)
        sys.exit(0)

    return signal_handler


def handle_signals(lock_file_path):
    for sig in [signal.SIGINT, signal.SIGTERM, signal.SIGQUIT, signal.SIGTSTP, signal.SIGABRT, signal.SIGILL,
                signal.SIGSEGV, signal.SIGFPE]:
        signal.signal(sig, make_signal_handler(lock_file_path))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(Errors.MISSING_CONFIG_FILE)
        sys.exit(1)
    elif len(sys.argv) > 2:
        print(Errors.TOO_MANY_ARGUMENTS)
        sys.exit(1)

    lock_file = handle_lock_file()

    if not lock_file[0]:
        print(Errors.PID_FILE_EXISTS.format(pid=lock_file[1]))
        sys.exit(1)

    handle_signals(lock_file[2])

    main(sys.argv[1:])
