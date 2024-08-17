import datetime
import json
import os
import signal
import subprocess
import sys
import time
import bisect
import zoneinfo

import psutil

import Constants
import Errors


class Task:
    days = Constants.DAYS_DICT

    def __init__(self, command, day_of_week, execution_time, title, description, *args):
        self.command = command

        if day_of_week.lower() not in self.days: # Check if the day of the week is valid
            raise ValueError(Errors.INVALID_DAY_OF_WEEK.format(day_of_week=day_of_week))

        self.day_of_week = day_of_week.lower()
        self.execution_time = execution_time
        self.title = title
        self.description = description
        self.args = args
        self.next_datetime = self.get_next_datetime()

    def get_next_datetime(self):
        # This method calculates the next datetime to run the task from now
        now = datetime.datetime.now(tz=zoneinfo.ZoneInfo(Constants.TIMEZONE))
        next_time = datetime.datetime.strptime(self.execution_time,
                                               Constants.TIME_FORMAT).time()  # gets only the time part
        day_gap = (self.days[self.day_of_week] - now.weekday()) % Constants.TOTAL_DAYS_OF_WEEK

        # If it's today but the time has passed, schedule for next week
        if day_gap == 0 and (now.time() >= next_time):
            day_gap = Constants.TOTAL_DAYS_OF_WEEK

        next_date = now.date() + datetime.timedelta(days=day_gap)

        return (datetime.datetime.combine(next_date, next_time)).replace(tzinfo=zoneinfo.ZoneInfo(Constants.TIMEZONE))


class Scheduler:
    def __init__(self):
        self.tasks = []

    def add_task(self, task: Task):
        # bisect insort based on task next_datetime
        # basically, insert into the tasks array, but insert it based on the task datetime order so the top of the list (stack)
        # is always the next task to run
        bisect.insort(self.tasks, (task.next_datetime, task))

    def get_next_task(self):
        if not self.tasks:
            return None

        next_task = self.tasks[0][1]  # Get the next task to run

        return next_task

    def run_tasks(self):
        while True:
            next_task = self.get_next_task()
            if next_task is None:
                print("No more tasks to run.")
                break

            now = datetime.datetime.now(tz=zoneinfo.ZoneInfo(Constants.TIMEZONE))
            time_to_wait = (next_task.next_datetime - now).total_seconds()

            if time_to_wait > 0:
                print(f"Waiting {time_to_wait} seconds until next task: {next_task.title}")
                time.sleep(time_to_wait)

            print(f"Running task: {next_task.title}")
            print(f"Description: {next_task.description}")

            subprocess.run([next_task.command, *next_task.args])
            next_task.next_datetime += datetime.timedelta(days=Constants.TOTAL_DAYS_OF_WEEK)
            self.add_task(next_task)
            self.tasks.pop(0) # Pop the current task from the list

    def has_next_task(self):
        return len(self.tasks) > 0


def parse_config(config_file):
    with open(config_file) as config:
        return json.load(config)


def schedule_tasks(scheduler, config_dict):
    for task in config_dict[Constants.CONFIG_DICT_SCHEDULE_KEY]:  # For every task in the config file
        scheduler.add_task(Task(task[Constants.CONFIG_DICT_COMMAND_KEY],  # Add the task to the scheduler
                                task[Constants.CONFIG_DICT_DAY_OF_WEEK_KEY],
                                task[Constants.CONFIG_DICT_TIME_KEY],
                                task[Constants.CONFIG_DICT_TITLE_KEY],  # Added title key to the config file
                                task[Constants.CONFIG_DICT_DESCRIPTION_KEY],  # Added description key to the config file
                                *task.get(Constants.CONFIG_DICT_ARGS_KEY, [])))


def main(args):
    config_location = args[0]  # Command line args
    config_dict = parse_config(config_location)  # Parses JSON into a Python dictionary
    scheduler = Scheduler()  # Initializes a scheduler object
    schedule_tasks(scheduler, config_dict)  # Schedules tasks based on the config file
    scheduler.run_tasks()  # Run the tasks that were parsed from the config file -- will run every week forever.


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
            pid = f.read().strip()

        try:
            pid = int(pid)

            if psutil.pid_exists(pid):
                print(Errors.PID_FILE_EXISTS.format(pid=pid))
                sys.exit(1)
            else:
                print(Constants.REMOVING_STALE_LOCK_FILE.format(lock_file_path))
                os.remove(lock_file_path)
        except ValueError:
            os.remove(lock_file_path)

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
    signals = Constants.WINDOWS_SIGNALS if os.name == Constants.WINDOWS_PLATFORM else Constants.POSIX_SIGNALS
    for sig in signals:
        signal.signal(sig, make_signal_handler(lock_file_path))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(Errors.MISSING_CONFIG_FILE)
        sys.exit(1)
    elif len(sys.argv) > 2:
        print(Errors.TOO_MANY_ARGUMENTS)
        sys.exit(1)

    lock_file = handle_lock_file()
    handle_signals(lock_file[2])

    try:
        main(sys.argv[1:])
    except Exception as e:
        print(e)
        os.remove(lock_file[2])
        sys.exit(1)
