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

LOCK_FILE_PATH_WINDOWS = 'C:\\ProgramData\\Scheduler\\.lock'
LOCK_FILE_PATH_LINUX = '/var/run/scheduler/.lock'
LOCK_FILE_PATH_MAC = '/var/run/scheduler/.lock'
LOCK_FILE_GENERIC = '.scheduler.lock'

WINDOWS_PLATFORM = 'nt'
LINUX_PLATFORM = 'posix'
MAC_PLATFORM = 'mac'

WINDOWS_SIGNALS = [signal.SIGINT, signal.SIGTERM, signal.SIGABRT, signal.SIGILL, signal.SIGSEGV, signal.SIGFPE]
POSIX_SIGNALS = [signal.SIGINT, signal.SIGTERM, signal.SIGABRT, signal.SIGILL, signal.SIGSEGV, signal.SIGFPE,
                 signal.SIGQUIT, signal.SIGHUP, signal.SIGTSTP]