import sys
from .websocket import client_tests, internal_tests
from . import __version__

if sys.argv[1] == 'version':
    print(__version__)
    sys.exit(0)

if sys.argv[1] == 'run_all_tests':
    print(f'Running all tests on version = {__version__}')
    username = sys.argv[2]
    password = sys.argv[3]
    live_port = None
    hist_port = None
    symbols = None
    try:
        for arg in sys.argv[4:]:
            if arg[:2] == "--":
                arg_split = arg[2:].split('=')
                arg_key = arg_split[0]
                arg_value = arg_split[1]
                if arg_key.lower() == 'liveport':
                    live_port = int(arg_value)
                if arg_key.lower() == 'histport':
                    hist_port = int(arg_value)
                if arg_key.lower() == 'symbols':
                    symbols = arg_value.split()
                    symbols = [symbol.strip() for symbol in symbols]
    except IndexError:
        pass
    client_tests.run_all_tests(username, password, live_port, hist_port, symbols)


if sys.argv[1] == 'run_internal_tests':
    print(f'The setup:\n'
          f'\tAccount A with live data = tick streaming, and bid-ask enabled in historic data.\n'
          f'\tAccount B with live data = 1min streaming, and no bid-ask in history.\n'
          f'\tThe live stream will run for 5 mins before terminating...')
    print(f'Running all tests on version = {__version__}')
    user_A = input('Enter User A username (1min streaming /wo bid-ask) - ')
    pass_A = input('Enter password for User A - ')
    user_B = input('Enter User B username (tick streaming /w bid-ask) - ')
    pass_B = input('Enter password for User B - ')
    live_port = None
    hist_port = None
    symbols = None
    try:
        for arg in sys.argv[2:]:
            if arg[:2] == "--":
                arg_split = arg[2:].split('=')
                arg_key = arg_split[0]
                arg_value = arg_split[1]
                if arg_key.lower() == 'liveport':
                    live_port = int(arg_value)
                if arg_key.lower() == 'histport':
                    hist_port = int(arg_value)
                if arg_key.lower() == 'symbols':
                    symbols = arg_value.split()
                    symbols = [symbol.strip() for symbol in symbols]
    except IndexError:
        pass
    internal_tests.run_all_tests(user_A, pass_A, user_B, pass_B, live_port, hist_port, symbols)

