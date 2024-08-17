# Task Scheduler
This is a simple task scheduler that can be used to schedule tasks to run on any system at any time. 
By simply configuring a JSON file, you can schedule commands to run at specific times every week on specific days.

# Purpose
I built this application to run bell schedules on VLC media player for a school I volunteer at. They asked me to 
automate the process of running the bell schedules at specific times every day instead of someone having to manually
go on and play the audio files every day at a specific time. 

With that being said, you may ask: "Why not use the built-in task scheduler on Windows?" or "Why not use X program on Y OS?"

These are both valid questions. Originally, we were planning to use the built-in task scheduler on Windows, but no matter what I did,
it would simply not play the task at the scheduled time. Ultimately, the time I was spending messing with Windows, it was
just easier to build my own task scheduler that I could control and understand. Likewise, I am sure various Unix systems have 
some preferred or recommended way of scheduling tasks. However, with this program, I can schedule tasks on virtually any operating system.

# How to Use
To use this program, you must install the following dependencies:
- Python 3.10 or higher (may work on lower versions, but I have not tested it)
- pip
- psutil
- tzdata

If you get any missing module errors, you may need to install them with pip using the following command:
```commandline
python3 -m pip install <module_name>
```

Once you have confirmed that you have all the dependencies installed, you can configure the `config.json` file to your liking.
The `config.json` is the file that will contain all the tasks that you want to schedule. You do not have to put the tasks in order of time,
this program will automatically sort the tasks by the time and day they are scheduled to run based on the `now` time (when you run the program).
Below is an example JSON file that you can configure to your liking. Simply just change the parameters in the schedule array to your liking. You can also
add new tasks into the schedule array and add as many as your heart desires (or as many tasks as your RAM has space for). I have not implemented any chunking
to loading the tasks, so if you have a lot of tasks, it may take a while to load them all into memory.

```json
{
    "schedule": [
        {
            "title": "Task1",
            "description": "Task1 Description",
            "day_of_week": "Monday",
            "time": "09:00",
            "command": "vlc",
            "args": [
                "--play-and-exit",
                "/some/video/file.mp3"
            ]
        },
        {
            "title": "Task2",
            "description": "Task2 Description",
            "day_of_week": "Tuesday",
            "time": "09:00",
            "command": "vlc",
            "args": [
                "--play-and-exit",
                "/some/video/file.mp3"
            ]
        },
        {
            "title": "Task3",
            "description": "Task3 Description",
            "day_of_week": "Wednesday",
            "time": "09:00",
            "command": "vlc",
            "args": [
                "--play-and-exit",
                "/some/video/file.mp3"
            ]
        }
    ]
}
```

The `args` command in each task is an array of arguments that will be passed to the command that you want to run. In the example above, I am running VLC media player
with the `--play-and-exit` flag and the path to the audio file that I want to play. You can change the command to whatever you want, but make sure that the command
is in your system's PATH or you have the full path to the command.

# Running the Program
Once you have configured your `config.json` to your liking, you can run the program by simply running the following command in the terminal:

```commandline
python3 scheduler.py <path_to_config.json>
```

If all goes well, you should see the program print out the next task that will be run and how long until that task will be run.

# Final Thoughts
If you have any questions, comments, or concerns about this program, feel free to make a GitHub issue and I'll respond to you as soon as I can.

I hope you find this program useful and that it helps you automate tasks on your system. If you have any suggestions for new features, feel free to let me know and I'll see if I can implement them.

Thanks for reading and happy scheduling!
