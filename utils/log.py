import os
import sys, inspect

import logging.config


class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

DEFAULT_LOGGING = {
    'version': 1,
    'formatters': {
        'standard': {
            'format': color.RED + '%(asctime)s,%(msecs)d' + color.END + color.PURPLE + ' %(levelname)-8s' + color.END + ' %(message)s',
            'datefmt': '%Y-%m-%d:%H:%M:%S' },
    },
    'handlers': {
        'console':  {'class': 'logging.StreamHandler',
                     'formatter': "standard",
                     'level': 'DEBUG',
                     'stream': sys.stdout},
        'file':     {'class': 'logging.FileHandler',
                     'formatter': "standard",
                     'level': 'DEBUG',
                     'filename': 'live_detector.log','mode': 'w'}
    },
    'loggers': {
        __name__:   {'level': 'INFO',
                     'handlers': ['console', 'file'],
                     'propagate': False },
    }
}

logging.config.dictConfig(DEFAULT_LOGGING)
log = logging.getLogger(__name__)

max_filename_length = 0

root_folder = os.path.dirname(os.path.dirname(inspect.currentframe().f_code.co_filename))

def log_function(func, msg: str, header=None, frame=None, traceback_length=5):
    global max_filename_length

    if not frame:
        frame = inspect.currentframe().f_back

    file_name = os.path.basename(frame.f_code.co_filename)
    line_no = str(frame.f_lineno)

    caller = ""

    for i in range(traceback_length):
        if frame is None:
            break

        temp_folder_name = os.path.dirname(frame.f_code.co_filename)

        if root_folder == temp_folder_name:
            caller = "(" + frame.f_code.co_name + ") " + caller

            frame = frame.f_back
        else:
            continue

    if caller:
        msg = color.GREEN + caller + color.END + msg

    if header:
        msg = color.YELLOW + header + color.END + msg

    filename_display = ' [' + file_name + ':' + line_no + '] '
    if len(filename_display) > max_filename_length:
        max_filename_length = len(filename_display)

    msg = color.CYAN + filename_display.ljust(max_filename_length) + color.END + msg

    func(msg)

def log_info(msg: str, header=None, frame=None, traceback_length=5):
    if frame:
        frame = frame.f_back
    else:
        frame = inspect.currentframe().f_back

    log_function(log.info, str(msg), header, frame, traceback_length)

def log_error(msg: str, header=None, frame=None, traceback_length=5):
    if frame:
        frame = frame.f_back
    else:
        frame = inspect.currentframe().f_back

    log_function(log.error, str(msg), header, frame, traceback_length)

def print_function_call(params=None, header=''):
    frame = inspect.currentframe().f_back

    if params:
        log_info("Called " + inspect.getmodule(frame).__name__ + "." + frame.f_code.co_name + " with parameters: " + str(params), header, frame)
    else:
        log_info("Called " + inspect.getmodule(frame).__name__ + "." + frame.f_code.co_name, header, frame)