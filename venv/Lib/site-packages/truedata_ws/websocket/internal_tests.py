from .base_tests import get_connection, run_live_tests, run_historical_tests
from .defaults import DEFAULT_LIVE_PORT, DEFAULT_HIST_PORT, DEFAULT_TEST_SYMBOL_LIST

from colorama import Style, Fore


def run_all_tests(user_a, pass_a, user_b, pass_b, live_port, historical_port, symbols_to_test):
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

    td_obj_with_bidask = get_connection(user_a, pass_a, live_port, historical_port)
    td_obj_without_bidask = get_connection(user_b, pass_b, live_port, historical_port)
    run_historical_tests(td_obj_with_bidask, symbols=symbols_to_test)
    run_historical_tests(td_obj_without_bidask, symbols=symbols_to_test)
