import os
import signal

DAYS_DICT = {  # Dictionary to convert day of week to integer
    'monday': 0,
    'tuesday': 1,
    'wednesday': 2,
    'thursday': 3,
    'friday': 4,
    'saturday': 5,
    'sunday': 6
}

TOTAL_DAYS_OF_WEEK = 7
TIME_FORMAT = '%H:%M'

CONFIG_DICT_COMMAND_KEY = 'command'
CONFIG_DICT_DAY_OF_WEEK_KEY = 'day_of_week'
CONFIG_DICT_SCHEDULE_KEY = 'schedule'
CONFIG_DICT_TIME_KEY = 'time'
CONFIG_DICT_ARGS_KEY = 'args'

WINDOWS_PLATFORM = 'nt'
LINUX_PLATFORM = 'posix'
MAC_PLATFORM = 'mac'

if os.name != WINDOWS_PLATFORM:
    POSIX_SIGNALS = [signal.SIGINT, signal.SIGTERM, signal.SIGABRT, signal.SIGILL, signal.SIGSEGV, signal.SIGFPE,
                     signal.SIGQUIT, signal.SIGHUP, signal.SIGTSTP]

    _runtime_dir = os.getenv('XDG_RUNTIME_DIR')
    if _runtime_dir:
        LOCK_FILE_PATH_LINUX = os.path.join(_runtime_dir, 'scheduler', '._lock')
        LOCK_FILE_PATH_MAC = os.path.join(_runtime_dir, 'scheduler', '._lock')
    else:
        # Fallback to home directory
        LOCK_FILE_PATH_LINUX = os.path.join(os.getenv('HOME'), 'scheduler', '._lock')
        LOCK_FILE_PATH_MAC = os.path.join(os.getenv('HOME'), 'scheduler', '_lock')
    LOCK_FILE_GENERIC = '.scheduler.lock'
else:
    WINDOWS_SIGNALS = [signal.SIGINT, signal.SIGTERM, signal.SIGABRT, signal.SIGILL, signal.SIGSEGV, signal.SIGFPE]
    LOCK_FILE_PATH_WINDOWS = os.path.join(os.getenv('LOCALAPPDATA'), 'Scheduler', '._lock')
