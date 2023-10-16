import datetime
import json
import subprocess
import sys
import time

tasks = []


class Task:
    days = {
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

        self.next_execution = datetime.datetime.strptime()



def run_task(command, *args):
    subprocess.call([command, *args])
    print(f"Task {command} completed successfully at {time.time()}")


def parse_config(config_file):
    with open(config_file) as f:
        config = json.load(f)

    return config


def schedule_tasks(config_dict):
    current_time = time.time()
    target_day = config_dict['day_of_week']


def main(args):
    config_location = args[0]
    config_dict = parse_config(config_location)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python scheduler.py <config_file>')
        sys.exit(1)
    elif len(sys.argv) > 2:
        print('Too many arguments!\nUsage: python scheduler.py <config_file>')
        sys.exit(1)

    main(sys.argv[1:])
