from . import websocket
from .websocket.defaults import MIN_PYTHON_MINOR, MIN_PYTHON_MAJOR, UPDATE_NOTIFICATION_SLEEP_TIME

import sys
import subprocess
from colorama import init, Style, Fore, Back
from time import sleep
from copy import deepcopy

from distutils import version

init()

__version__ = '1.0.1'
update_notification_sleep_time = deepcopy(UPDATE_NOTIFICATION_SLEEP_TIME)

try:
    user_python_version = sys.version_info
    if not (user_python_version.major >= MIN_PYTHON_MAJOR and user_python_version.minor >= MIN_PYTHON_MINOR):
        print(f"{Style.BRIGHT}{Fore.RED}\tIt is highly advised that you use Python {MIN_PYTHON_MAJOR}.{MIN_PYTHON_MINOR} or greater...\n"
              f"\tSome features may not work as intended on your version ({user_python_version.major}.{user_python_version.minor}.{user_python_version.micro})...{Style.RESET_ALL}")
        print(f"\tPlease decide if you want to proceed with running as is or not...\n")
        wrong_version_warning_input = input(f"\tReply with: {Back.CYAN}{Fore.BLACK}Y/N{Style.RESET_ALL} (Anything other than {Back.CYAN}{Fore.BLACK}Y{Style.RESET_ALL} will exit the code) : ")
        if wrong_version_warning_input.upper()[0] != "Y":
            exit()
except Exception as e:
    print(f'{Style.BRIGHT}{Fore.RED}\tUnable to get the version of Python you are using...\n'
          f'\tPlease report this error to truedata...\n'
          f'\tAlong with the following information - {e}...{Style.RESET_ALL}')
try:
    op = subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'truedata_ws=='], capture_output=True)
    latest_version = max([version.StrictVersion(i.strip()) for i in str(op.stderr).split('from versions:')[1].split(')')[0].split(',')])
    if latest_version > version.StrictVersion(__version__):
        if version.StrictVersion(__version__) < version.StrictVersion('0.1.0'):
            update_notification_sleep_time = 0
        if update_notification_sleep_time > 0:
            print(f"{Style.BRIGHT}{Fore.GREEN}\tThere is a newer version of this library available ({latest_version}), while your version is {__version__}...\n"
                  f"\tIt is highly advisable that you keep your libraries up-to-date... Please upgrade your library using-\n"
                  f"\n\t\t python3.7 -m pip install --upgrade truedata_ws\n"
                  f"\tWe also strongly recommend you read our release notes at the end of the README.md that is found at the end of PyPi page (found at: https://pypi.org/project/truedata-ws/){Style.RESET_ALL}")
        while update_notification_sleep_time > 0:
            sleep(1)
            print(f'{Style.BRIGHT}{Fore.GREEN}Your code will resume in {update_notification_sleep_time} secs...{Style.RESET_ALL}', end='\r')
            update_notification_sleep_time = update_notification_sleep_time - 1
except Exception as e:
    print(f'{Style.BRIGHT}{Fore.RED}\tUnable to get latest version from PyPi...\n'
          f'\tPlease report this error to truedata...\n'  # TODO: If no error reported within a month, add this -  or raise an issue on https://github.com/paritoshjchandran/truedata/issues/new
          f'\tAlong with the following information - {e}...{Style.RESET_ALL}')
