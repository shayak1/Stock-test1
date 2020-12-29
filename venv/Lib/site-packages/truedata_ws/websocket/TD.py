from websocket import WebSocketApp, create_connection
from .support import TickLiveData, MinLiveData, TouchlineData

from threading import Thread

from datetime import datetime
from dateutil.relativedelta import relativedelta
import json
import time
from functools import wraps

from colorama import Style, Fore
from builtins import TimeoutError, ConnectionResetError
from copy import deepcopy

DEFAULT_HISTORIC_DATA_ID = 1000
DEFAULT_MARKET_DATA_ID = 2000


class TDHistoricDataError(Exception):
    def __str__(self):
        return f"{Style.BRIGHT}{Fore.RED}Something's wrong with the historical data...{Style.RESET_ALL}"


class TDLiveDataError(Exception):
    def __str__(self):
        return f"{Style.BRIGHT}{Fore.RED}Something's wrong with the historical data...{Style.RESET_ALL}"


class TDInvalidRequestError(Exception):
    def __str__(self):
        return f"{Style.BRIGHT}{Fore.RED}Invalid request{Style.RESET_ALL}"


def historical_decorator(func):
    @wraps(func)
    def dec_helper(obj, contract, end_time, start_time, bar_size, options=None):
        options = {}
        if bar_size.lower() == 'tick':
            bar_size = 'tick'
            options['time_format'] = '%Y-%m-%dT%H:%M:%S'
            options['processor_to_call'] = obj.hist_tick_data_to_dict_list
        elif bar_size.lower() == 'eod':
            start_time = start_time.split('T')[0]
            end_time = end_time.split('T')[0]
            bar_size = 'EOD'
            options['time_format'] = '%Y-%m-%d'
            options['processor_to_call'] = obj.hist_bar_data_to_dict_list
        else:
            bar_size = bar_size.replace(' ', '')
            if bar_size[-1] == 's':
                bar_size = bar_size[:-1]
            options['time_format'] = '%Y-%m-%dT%H:%M:%S'
            options['processor_to_call'] = obj.hist_bar_data_to_dict_list
        return func(obj, contract, end_time, start_time, bar_size, options)
    return dec_helper


class LiveClient(WebSocketApp):

    def __init__(self, parent_app, url, *args):
        WebSocketApp.__init__(self, url, on_open=self.ws_open, on_error=self.ws_error, on_message=self.on_msg_func, *args)
        self.segments = []
        self.max_symbols = 0
        self.remaining_symbols = 0
        self.valid_until = ''
        self.contract_mapping = {}
        self.subscription_type = ''
        self.confirm_heartbeats = 1
        self.store_last_n_heartbeats = self.confirm_heartbeats + 7
        self.heartbeat_interval = 5
        self.heartbeat_buffer = 0.5
        time_of_creation = datetime.now()
        self.last_n_heartbeat = [time_of_creation - relativedelta(seconds=i * self.heartbeat_interval) for i in range(-self.store_last_n_heartbeats, 0)]
        self.parent_app = parent_app
        self.disconnect_flag = False
        self.heartbeat_check_thread = Thread(target=self.check_heartbeat)
        if self.parent_app.live_port == 8086 or self.parent_app.live_port == 8084:
            self.heartbeat_check_thread.start()

    def check_connection(self):
        base_heartbeat = self.last_n_heartbeat[-self.confirm_heartbeats]
        check_time = datetime.now()
        time_diff = check_time - base_heartbeat
        is_connected = time_diff.total_seconds() > ((self.heartbeat_interval + self.heartbeat_buffer) * self.confirm_heartbeats)  # 3 > 5 + 0.5
        return is_connected

    def check_heartbeat(self):
        while True:
            time.sleep(self.heartbeat_interval)
            if self.disconnect_flag:
                print(f"{Fore.GREEN}Removing hand from the pulse...{Style.RESET_ALL}")
                break
            if self.check_connection():
                print(f"{Style.BRIGHT}{Fore.RED}Failed Heartbeat @ {datetime.now()} because of last at {self.last_n_heartbeat[-self.confirm_heartbeats]}{Style.RESET_ALL}")
                print(f"{Style.BRIGHT}{Fore.RED}Attempting reconnect @ {Fore.CYAN}{datetime.now()}{Style.RESET_ALL}")
                restart_successful = self.reconnect()
                if restart_successful:
                    print(f"{Style.BRIGHT}{Fore.GREEN}Successful restart @ {Fore.CYAN}{datetime.now()}{Style.RESET_ALL}")
                    time.sleep((self.heartbeat_interval + self.heartbeat_buffer))
                    recover_start, recover_end = self.get_largest_diff(self.last_n_heartbeat)
                    # print(f"\t\t\t{len(self.last_n_heartbeat)} - {self.last_n_heartbeat}")
                    self.recover_from_time_missed(recover_start, recover_end)
                else:
                    print(f"{Style.BRIGHT}{Fore.RED}Failed restart @ {Fore.CYAN}{datetime.now()}{Style.RESET_ALL}")

    @staticmethod
    def get_largest_diff(time_series):
        big_li = deepcopy(time_series.pop(0))
        small_li = deepcopy(time_series.pop())
        diffs = [i[0]-i[1] for i in zip(big_li, small_li)]
        start_gap_index = max(range(len(diffs)), key=lambda i: diffs[i])
        return time_series[start_gap_index], time_series[start_gap_index+1]

    def recover_from_time_missed(self, start_time, end_time):
        print(f"{Style.BRIGHT}{Fore.YELLOW}Initiating recovery from {Fore.GREEN}{start_time}{Fore.YELLOW} till {Fore.GREEN}{end_time}{Fore.YELLOW} which are last green heartbeats from server...{Style.RESET_ALL}")

    def reconnect(self):
        self.close()
        t = Thread(target=self.run_forever)
        t.start()
        time.sleep(1)
        is_td_connected = False
        while not is_td_connected:
            time.sleep(self.heartbeat_interval + self.heartbeat_buffer)
            is_td_connected = self.check_connection()
        return is_td_connected

    def on_msg_func(self, message):
        msg = json.loads(message)
        if 'message' in msg.keys():
            self.handle_message_data(msg)
        if 'trade' in msg.keys():
            trade = msg['trade']
            self.handle_trade_data(trade)
        elif 'bidask' in msg.keys():
            bidask = msg['bidask']
            self.handle_bid_ask_data(bidask)
        elif any(['min' in key for key in msg.keys()]):
            bar_key = next(key for key in msg.keys() if 'min' in key)
            bar_data = msg[bar_key]
            self.handle_bar_data(bar_data)

    def handle_message_data(self, msg):
        if msg['success']:
            if msg['message'] == 'HeartBeat':
                self.handle_heartbeat(msg['timestamp'])
            elif msg['message'] == 'TrueData Real Time Data Service':  # Connection success message
                print(f"You have subscribed for {msg['maxsymbols']} symbols across {msg['segments']} until {msg['validity']} with type of stream as {msg['subscription']}...")
                self.subscription_type = msg['subscription']
            elif msg['message'] == 'symbols added':
                self.add_contract_details(msg['symbollist'])
            elif msg['message'] == 'symbols removed':
                self.remove_symbols(msg['symbollist'])
        else:
            print(f"{Style.BRIGHT}{Fore.RED}The request encountered an error - {msg['message']}{Style.RESET_ALL}")

    def handle_heartbeat(self, server_timestamp):
        timestamp = datetime.strptime(server_timestamp + ((26 - len(server_timestamp)) * "0"), "%Y-%m-%d %H:%M:%S.%f")
        self.last_n_heartbeat = self.last_n_heartbeat[1:]
        self.last_n_heartbeat.append(timestamp)

    def remove_symbols(self, contracts):
        for contract_info in contracts:
            contract = contract_info.split(':')[0]
            for req_id in self.parent_app.symbol_mkt_id_map[contract.upper()]:
                del self.parent_app.live_data[req_id]
            del self.parent_app.symbol_mkt_id_map[contract.upper()]

    def add_contract_details(self, contracts_list):
        for contract in contracts_list:
            if contract is not None:
                contract_details = contract.split(':')
                self.contract_mapping[int(contract_details[1])] = symbol = contract_details[0]
                for ticker_id in self.parent_app.symbol_mkt_id_map[symbol]:
                    self.parent_app.touchline_data[ticker_id].symbol = symbol
                    self.parent_app.touchline_data[ticker_id].symbol_id = int(contract_details[1])
                    self.parent_app.touchline_data[ticker_id].open = float(contract_details[2])
                    self.parent_app.touchline_data[ticker_id].high = float(contract_details[3])
                    self.parent_app.touchline_data[ticker_id].low = float(contract_details[4])
                    self.parent_app.touchline_data[ticker_id].ltp = float(contract_details[5])
                    self.parent_app.touchline_data[ticker_id].prev_close = float(contract_details[6])
                    self.parent_app.touchline_data[ticker_id].ttq = int(contract_details[7])
                    self.parent_app.touchline_data[ticker_id].oi = int(contract_details[8])
                    self.parent_app.touchline_data[ticker_id].prev_oi = int(contract_details[9])
                    self.parent_app.touchline_data[ticker_id].turnover = float(contract_details[10])
                    self.parent_app.live_data[ticker_id].tick_type = 0
                    self.parent_app.live_data[ticker_id].populate_using_touchline(self.parent_app.touchline_data[ticker_id])
            else:
                print(f'{Style.BRIGHT}{Fore.YELLOW}Probable repeated symbol...{Style.RESET_ALL}')

    def handle_trade_data(self, trade_tick):
        try:
            symbol = self.contract_mapping[int(trade_tick[0])]
            for ticker_id in self.parent_app.symbol_mkt_id_map[symbol]:
                # Assigning new data
                self.parent_app.live_data[ticker_id].symbol_id = int(trade_tick[0])
                self.parent_app.live_data[ticker_id].timestamp = datetime.strptime(trade_tick[1], '%Y-%m-%dT%H:%M:%S')  # Old format = '%m/%d/%Y %I:%M:%S %p'
                self.parent_app.live_data[ticker_id].symbol = symbol
                self.parent_app.live_data[ticker_id].ltp = self.parent_app.touchline_data[ticker_id].ltp = ltp = float(trade_tick[2])
                self.parent_app.live_data[ticker_id].volume = float(trade_tick[3])
                self.parent_app.live_data[ticker_id].atp = float(trade_tick[4])
                self.parent_app.live_data[ticker_id].oi = float(trade_tick[5])
                self.parent_app.live_data[ticker_id].ttq = float(trade_tick[6])
                self.parent_app.live_data[ticker_id].special_tag = special_tag = str(trade_tick[7])
                if special_tag != "":
                    if special_tag == 'H':
                        self.parent_app.live_data[ticker_id].day_high = self.parent_app.touchline_data[ticker_id].high = ltp
                    elif special_tag == 'L':
                        self.parent_app.live_data[ticker_id].day_low = self.parent_app.touchline_data[ticker_id].low = ltp
                    elif special_tag == 'O':
                        self.parent_app.live_data[ticker_id].day_open = self.parent_app.touchline_data[ticker_id].open = ltp
                self.parent_app.live_data[ticker_id].tick_seq = int(trade_tick[8])
                self.parent_app.live_data[ticker_id].tick_type = 1
                # Calculating addn data
                self.parent_app.live_data[ticker_id].calculate_additional_data()
                try:
                    self.parent_app.live_data[ticker_id].best_bid_price = float(trade_tick[9])
                    self.parent_app.live_data[ticker_id].best_bid_qty = int(trade_tick[10])
                    self.parent_app.live_data[ticker_id].best_ask_price = float(trade_tick[11])
                    self.parent_app.live_data[ticker_id].best_ask_qty = int(trade_tick[12])
                except (IndexError, ValueError, TypeError):
                    try:
                        del self.parent_app.live_data[ticker_id].best_bid_price
                        del self.parent_app.live_data[ticker_id].best_bid_qty
                        del self.parent_app.live_data[ticker_id].best_ask_price
                        del self.parent_app.live_data[ticker_id].best_ask_qty
                    except AttributeError:
                        pass
                except Exception as e:
                    print(e)
        except KeyError:
            pass
        except Exception as e:
            print(f'{Style.BRIGHT}{Fore.RED}Encountered with tick feed - {type(e)}{Style.RESET_ALL}')

    def handle_bid_ask_data(self, bidask_tick):
        try:
            symbol = self.contract_mapping[int(bidask_tick[0])]
            for ticker_id in self.parent_app.symbol_mkt_id_map[symbol]:
                self.parent_app.live_data[ticker_id].symbol_id = int(bidask_tick[0])
                self.parent_app.live_data[ticker_id].timestamp = datetime.strptime(bidask_tick[1], '%Y-%m-%dT%H:%M:%S')
                self.parent_app.live_data[ticker_id].best_bid_price = float(bidask_tick[2])
                self.parent_app.live_data[ticker_id].best_bid_qty = int(bidask_tick[3])
                self.parent_app.live_data[ticker_id].best_ask_price = float(bidask_tick[4])
                self.parent_app.live_data[ticker_id].best_ask_qty = int(bidask_tick[5])
                self.parent_app.live_data[ticker_id].tick_type = 2
        except KeyError:
            pass
        except Exception as e:
            print(f'{Style.BRIGHT}{Fore.RED}Encountered with bid-ask feed - {e}{Style.RESET_ALL}')

    def handle_bar_data(self, bar_data):
        try:
            symbol = self.contract_mapping[int(bar_data[0])]
            for ticker_id in self.parent_app.symbol_mkt_id_map[symbol]:
                # Assigning new data
                self.parent_app.live_data[ticker_id].symbol_id = int(bar_data[0])
                self.parent_app.live_data[ticker_id].timestamp = datetime.strptime(bar_data[1], '%Y-%m-%dT%H:%M:%S')
                self.parent_app.live_data[ticker_id].symbol = symbol
                self.parent_app.live_data[ticker_id].open = float(bar_data[2])
                self.parent_app.live_data[ticker_id].high = bar_high = float(bar_data[3])
                if bar_high > self.parent_app.live_data[ticker_id].day_high:
                    self.parent_app.live_data[ticker_id].day_high = self.parent_app.touchline_data[ticker_id].high = bar_high
                self.parent_app.live_data[ticker_id].low = bar_low = float(bar_data[4])
                if bar_low < self.parent_app.live_data[ticker_id].day_low:
                    self.parent_app.live_data[ticker_id].day_low = self.parent_app.touchline_data[ticker_id].low = bar_low
                self.parent_app.live_data[ticker_id].close = self.parent_app.touchline_data[ticker_id].ltp = float(bar_data[5])
                self.parent_app.live_data[ticker_id].volume = float(bar_data[6])
                self.parent_app.live_data[ticker_id].oi = float(bar_data[7])
                # Calculating addn data
                self.parent_app.live_data[ticker_id].calculate_additional_data()
        except KeyError:
            pass
        except Exception as e:
            print(f'{Style.BRIGHT}{Fore.RED}Encountered with bar feed - {e}{Style.RESET_ALL}')

    def ws_error(self, error):
        if any(isinstance(error, conn_error) for conn_error in [ConnectionResetError, TimeoutError]):
            print(error)

    def ws_open(self):
        self.sock.settimeout(300)


class HistoricalWebsocket:
    def __init__(self, login_id, password, url, historical_port, broker_token):
        self.login_id = login_id
        self.password = password
        self.url = url
        self.historical_port = historical_port
        self.broker_token = broker_token
        broker_append = ''
        if self.broker_token is not None:
            broker_append = f'&brokertoken={self.broker_token}'
        self.hist_socket = create_connection(f"wss://{self.url}:{self.historical_port}?user={self.login_id}&password={self.password}{broker_append}")
        welcome_msg = self.hist_socket.recv()
        welcome_msg = json.loads(welcome_msg)
        if welcome_msg['success']:
            print(f"Connected successfully to {welcome_msg['message']}")
        else:
            print(f"{Style.BRIGHT}{Fore.RED}Failed to connect with error message = {welcome_msg['message']}{Style.RESET_ALL}")
            self.hist_socket.close()

    def get_n_historic_bars(self, contract, end_time, no_of_bars, bar_size):
        if bar_size.lower() != 'eod' and bar_size.lower() != 'tick':
            bar_size = bar_size.replace(' ', '')
            if bar_size[-1] == 's':
                bar_size = bar_size[:-1]
        self.hist_socket.send(f'{{"method": "gethistorylastnbars", "interval": "{bar_size}", "symbol": "{contract}", "nbars": "{no_of_bars}", "to": "{end_time}"}}')
        raw_hist_data = self.hist_socket.recv()
        json_response = json.loads(raw_hist_data)
        if json_response['success']:
            hist_data = json_response['data']
            if bar_size.lower() == 'tick':
                hist_data = self.hist_tick_data_to_dict_list(hist_data, '%Y-%m-%dT%H:%M:%S')
            elif bar_size.lower() == 'eod':
                hist_data = self.hist_bar_data_to_dict_list(hist_data, '%Y-%m-%d')
            else:
                hist_data = self.hist_bar_data_to_dict_list(hist_data, '%Y-%m-%dT%H:%M:%S')
            return hist_data
        else:
            print(f'{Style.BRIGHT}{Fore.RED}ERROR: Your request failed with error "{json_response["message"]}"{Style.RESET_ALL}')
            return []

    @historical_decorator
    def get_historic_data(self, contract, end_time, start_time, bar_size, options=None):
        self.hist_socket.send(f'{{"method": "gethistory", "interval": "{bar_size}", "symbol": "{contract}", "from": "{start_time}", "to": "{end_time}"}}')
        
        def dive_for_data(hd_socket):
            dive_raw_data = hd_socket.recv()
            try:
                dive_response = json.loads(dive_raw_data)
            except json.decoder.JSONDecodeError:
                print(f'{Style.BRIGHT}{Fore.RED}{{"method": "gethistory", "interval": "{bar_size}", "symbol": "{contract}", "from": "{start_time}", "to": "{end_time}"}}{Style.RESET_ALL}')
                print(f'{dive_raw_data}')
                return []
            if dive_response['success']:
                try:
                    if dive_response['message'] == 'HeartBeat':
                        return dive_for_data(hd_socket)
                except KeyError:
                    return dive_response['data']
            else:
                print(f'{Style.BRIGHT}{Fore.RED}ERROR: Your request failed with error "{dive_response["message"]}"{Style.RESET_ALL}')
                return []

        hist_data = dive_for_data(self.hist_socket)
        hist_data = options['processor_to_call'](hist_data, time_format=options['time_format'])
        return hist_data

    @staticmethod
    def hist_tick_data_to_dict_list(hist_data, time_format):
        data_list = []
        count = 0
        for j in hist_data:
            try:
                data_list.append({'time': datetime.strptime(j[0], time_format),
                                  'ltp': float(j[1]),
                                  'volume': int(j[2]),
                                  'oi': int(j[3]),
                                  'bid': float(j[4]),
                                  'bid_qty': int(j[5]),
                                  'ask': float(j[6]),
                                  'ask_qty': int(j[7])})
            except IndexError:  # No bid-ask data
                data_list.append({'time': datetime.strptime(j[0], time_format),
                                  'ltp': float(j[1]),
                                  'volume': int(j[2]),
                                  'oi': int(j[3])})
                continue
            count = count + 1
        return data_list

    @staticmethod
    def hist_bar_data_to_dict_list(hist_data, time_format):
        data_list = []
        
        for j in hist_data:
            data_list.append({'time': datetime.strptime(j[0], time_format),
                              'o': float(j[1]),
                              'h': float(j[2]),
                              'l': float(j[3]),
                              'c': float(j[4]),
                              'v': int(j[5]),
                              'oi': int(j[6])})
        return data_list


class TD:
    def __init__(self, login_id, password, broker_token=None, url='push.truedata.in', live_port=8082, historical_port=8092, *args):
        self.live_websocket = None
        self.historical_websocket = None
        self.login_id = login_id
        self.password = password
        self.url = url
        self.live_port = live_port
        self.historical_port = historical_port
        if historical_port is None:
            self.connect_historical = False
        else:
            self.connect_historical = True
        self.broker_token = broker_token
        self.hist_data = {}
        self.live_data = {}
        self.symbol_mkt_id_map = {}
        self.streaming_symbols = {}
        self.touchline_data = {}
        self.connect()

    def connect(self):
        broker_append = ''
        if self.broker_token is not None:
            broker_append = f'&brokertoken={self.broker_token}'
        self.live_websocket = LiveClient(self, f"wss://{self.url}:{self.live_port}?user={self.login_id}&password={self.password}{broker_append}")
        t = Thread(target=self.connect_thread, args=())
        t.start()
        if self.connect_historical:
            self.historical_websocket = HistoricalWebsocket(self.login_id, self.password, self.url, self.historical_port, self.broker_token)
        while self.live_websocket.subscription_type == '':
            time.sleep(1)

    def connect_thread(self):
        self.live_websocket.run_forever()

    def disconnect(self):
        self.live_websocket.disconnect_flag = True
        self.live_websocket.close()
        print(f"{Fore.GREEN}Disconnected LIVE TrueData...{Style.RESET_ALL}")
        if self.connect_historical:
            self.historical_websocket.hist_socket.close()
            print(f"{Fore.GREEN}Disconnected HISTORICAL TrueData...{Style.RESET_ALL}")

    @staticmethod
    def truedata_duration_map(regular_format, end_date):
        duration_units = regular_format.split()[1].upper()
        if len(duration_units) > 1:
            raise TDHistoricDataError
        duration_size = int(regular_format.split()[0])
        if duration_units == 'D':
            return (end_date - relativedelta(days=duration_size - 1)).date()
        elif duration_units == 'W':
            return (end_date - relativedelta(weeks=duration_size)).date()
        elif duration_units == 'M':
            return (end_date - relativedelta(months=duration_size)).date()
        elif duration_units == 'Y':
            return (end_date - relativedelta(years=duration_size)).date()

    def get_historic_data(self, contract,
                          ticker_id=DEFAULT_HISTORIC_DATA_ID,
                          end_time=None,
                          duration=None,
                          start_time=None,
                          bar_size="1 min"):
        global DEFAULT_HISTORIC_DATA_ID
        if start_time is not None and duration is None:
            return self.get_historical_data_from_start_time(contract=contract,
                                                            ticker_id=ticker_id,
                                                            end_time=end_time,
                                                            start_time=start_time,
                                                            bar_size=bar_size)
        else:
            return self.get_historical_data_from_duration(contract=contract,
                                                          ticker_id=ticker_id,
                                                          end_time=end_time,
                                                          duration=duration,
                                                          bar_size=bar_size)

    def get_n_historical_bars(self, contract,
                              ticker_id=DEFAULT_HISTORIC_DATA_ID,
                              end_time=None,
                              no_of_bars: int = 1,
                              bar_size="1 min"):
        global DEFAULT_HISTORIC_DATA_ID
        if end_time is None:
            end_time = datetime.today()
        else:
            assert type(end_time) == datetime
        end_time = end_time.strftime('%Y-%m-%dT%H:%M:%S')
        hist_data = self.historical_websocket.get_n_historic_bars(contract, end_time, no_of_bars, bar_size)
        DEFAULT_HISTORIC_DATA_ID = DEFAULT_HISTORIC_DATA_ID + 1
        self.hist_data[ticker_id] = hist_data
        return hist_data

    def get_historical_data_from_duration(self, contract,
                                          ticker_id=DEFAULT_HISTORIC_DATA_ID,
                                          end_time=None,
                                          duration=None,
                                          bar_size="1 min"):
        global DEFAULT_HISTORIC_DATA_ID
        if duration is None:
            duration = "1 D"
        if end_time is None:
            end_time = datetime.today()
        else:
            assert type(end_time) == datetime
        start_time = self.truedata_duration_map(duration, end_time)
        end_time = end_time.strftime('%Y-%m-%d') + 'T23:59:59'
        start_time = start_time.strftime('%Y-%m-%d') + 'T00:00:00'

        hist_data = self.historical_websocket.get_historic_data(contract, end_time, start_time, bar_size)
        DEFAULT_HISTORIC_DATA_ID = DEFAULT_HISTORIC_DATA_ID + 1
        self.hist_data[ticker_id] = hist_data
        return hist_data

    def get_historical_data_from_start_time(self, contract,
                                            ticker_id=DEFAULT_HISTORIC_DATA_ID,
                                            end_time=None,
                                            start_time=None,
                                            bar_size="1 min"):
        global DEFAULT_HISTORIC_DATA_ID
        if end_time is None:
            end_time = datetime.today().replace(hour=23, minute=59, second=59)
        else:
            assert type(end_time) == datetime
        if start_time is None:
            start_time = datetime.today().replace(hour=0, minute=0, second=0)
        else:
            assert type(start_time) == datetime

        end_time = end_time.strftime('%Y-%m-%dT%H:%M:%S')
        start_time = start_time.strftime('%Y-%m-%dT%H:%M:%S')
        hist_data = self.historical_websocket.get_historic_data(contract, end_time, start_time, bar_size)
        DEFAULT_HISTORIC_DATA_ID = DEFAULT_HISTORIC_DATA_ID + 1
        self.hist_data[ticker_id] = hist_data
        return hist_data

    def start_live_data(self, resolved_contracts, req_id=None):
        global DEFAULT_MARKET_DATA_ID
        if req_id is None:
            req_id = DEFAULT_MARKET_DATA_ID

        req_ids = []
        if type(req_id) == list:
            if len(req_id) == len(resolved_contracts):
                req_ids = req_id
            else:
                print(f"{Style.BRIGHT}{Fore.RED}Lengths do not match...{Style.RESET_ALL}")
        elif req_id is None:
            curr_req_id = DEFAULT_MARKET_DATA_ID
            for i in range(0, len(resolved_contracts)):
                req_ids.append(curr_req_id + i)
            DEFAULT_MARKET_DATA_ID = DEFAULT_MARKET_DATA_ID + len(resolved_contracts)
        elif type(req_id) == int:
            curr_req_id = req_id
            for i in range(0, len(resolved_contracts)):
                req_ids.append(curr_req_id + i)
        else:
            print(f"{Style.BRIGHT}{Fore.RED}Invalid req_id datatype...{Style.RESET_ALL}")
            raise TDLiveDataError
        for j in range(0, len(req_ids)):
            resolved_contract = resolved_contracts[j].upper()
            self.touchline_data[req_ids[j]] = TouchlineData()
            if self.live_websocket.subscription_type == 'tick':
                self.live_data[req_ids[j]] = TickLiveData(resolved_contract)
            elif 'min' in self.live_websocket.subscription_type:
                self.live_data[req_ids[j]] = MinLiveData(resolved_contract)
                print(req_ids[j])
            try:
                self.symbol_mkt_id_map[resolved_contract].append(req_ids[j])
            except KeyError:
                self.symbol_mkt_id_map[resolved_contract] = [req_ids[j]]
        self.live_websocket.send(f'{{"method": "addsymbol", "symbols": {json.dumps(resolved_contracts)}}}')
        return req_ids

    def stop_live_data(self, contracts):
        self.live_websocket.send(f'{{"method": "removesymbol", "symbols": {json.dumps(contracts)}}}')

    def get_touchline(self):
        self.live_websocket.send(f'{{"method": "touchline"}}')
