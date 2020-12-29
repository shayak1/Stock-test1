from .defaults import DEFAULT_LIVE_PORT, DEFAULT_HIST_PORT, DEFAULT_TEST_SYMBOL_LIST
from .base_tests import get_connection, run_historical_tests, run_live_tests

from colorama import Style, Fore


def run_all_tests(username, password, live_port=None, historical_port=None, symbols_to_test=None):
    if live_port is None:
        print(f'{Style.BRIGHT}{Fore.BLUE}Setting to default live port = {DEFAULT_LIVE_PORT}{Style.RESET_ALL}')
        live_port = DEFAULT_LIVE_PORT
    else:
        print(f'{Style.BRIGHT}{Fore.BLUE}Using given live port = {live_port}{Style.RESET_ALL}')
    if historical_port is None:
        print(f'{Style.BRIGHT}{Fore.BLUE}Setting to default hist port = {DEFAULT_HIST_PORT}{Style.RESET_ALL}')
        historical_port = DEFAULT_HIST_PORT
    else:
        print(f'{Style.BRIGHT}{Fore.BLUE}Using given historical port = {historical_port}{Style.RESET_ALL}')
    if symbols_to_test is None:
        print(f'{Style.BRIGHT}{Fore.BLUE}Setting to default symbol list = {DEFAULT_TEST_SYMBOL_LIST}{Style.RESET_ALL}')
        symbols_to_test = DEFAULT_TEST_SYMBOL_LIST
    else:
        print(f'{Style.BRIGHT}{Fore.BLUE}Using given symbol list = {symbols_to_test}{Style.RESET_ALL}')

    print(f'{Style.BRIGHT}{Fore.BLUE}Beginning connection test...{Style.RESET_ALL}')
    td_app = get_connection(username, password, live_port, historical_port)

    print(f'{Style.BRIGHT}{Fore.BLUE}Beginning historical data test...{Style.RESET_ALL}')
    run_historical_tests(td_app, symbols_to_test)

    print(f'{Style.BRIGHT}{Fore.BLUE}Beginning live data test...{Style.RESET_ALL}')
    run_live_tests(td_app, symbols_to_test)


def run_live_tests(username, password, live_port=None, historical_port=None, symbols_to_test=None):
    if live_port is None:
        print(f'{Style.BRIGHT}{Fore.BLUE}Setting to default live port = {DEFAULT_LIVE_PORT}{Style.RESET_ALL}')
        live_port = DEFAULT_LIVE_PORT
    else:
        print(f'{Style.BRIGHT}{Fore.BLUE}Using given live port = {live_port}{Style.RESET_ALL}')
    if historical_port is None:
        print(f'{Style.BRIGHT}{Fore.BLUE}Setting to default hist port = {DEFAULT_HIST_PORT}{Style.RESET_ALL}')
        historical_port = DEFAULT_HIST_PORT
    else:
        print(f'{Style.BRIGHT}{Fore.BLUE}Using given historical port = {historical_port}{Style.RESET_ALL}')
    if symbols_to_test is None:
        print(f'{Style.BRIGHT}{Fore.BLUE}Setting to default symbol list = {DEFAULT_TEST_SYMBOL_LIST}{Style.RESET_ALL}')
        symbols_to_test = DEFAULT_TEST_SYMBOL_LIST
    else:
        print(f'{Style.BRIGHT}{Fore.BLUE}Using given symbol list = {symbols_to_test}{Style.RESET_ALL}')

    print(f'{Style.BRIGHT}{Fore.BLUE}Beginning connection test...{Style.RESET_ALL}')
    td_app = get_connection(username, password, live_port, historical_port)

    print(f'{Style.BRIGHT}{Fore.BLUE}Beginning live data test...{Style.RESET_ALL}')
    run_live_tests(td_app, symbols_to_test)
