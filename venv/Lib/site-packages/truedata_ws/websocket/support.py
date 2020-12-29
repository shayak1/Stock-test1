from datetime import datetime
from colorama import Style, Fore


class TouchlineData:
    def __init__(self):
        self.symbol = None
        self.symbol_id = None
        self.open = None
        self.high = None
        self.low = None
        self.ltp = None
        self.prev_close = None
        self.ttq = None
        self.oi = None
        self.prev_oi = None
        self.turnover = None

    def __str__(self):
        return str(self.__dict__)


class TickLiveData:
    def __init__(self, symbol):
        # --Common Variables
        self.timestamp = None
        self.symbol = symbol
        self.symbol_id = None
        self.day_high = None
        self.day_low = None
        self.day_open = None
        self.prev_day_close = None
        self.prev_day_oi = None
        self.oi = None
        self.ttq = None
        # --Obj specific
        self.ltp = None
        self.atp = None
        self.volume = None
        self.special_tag = ""
        self.tick_seq = None
        self.best_bid_price = None
        self.best_bid_qty = None
        self.best_ask_price = None
        self.best_ask_qty = None
        self.tick_type = None  # 0 -> touchline | 1 -> trade | 2 -> bidask
        # -- Calculated common
        self.change = None
        self.change_perc = None
        self.oi_change = None
        self.oi_change_perc = None
        # -- Calculated specific
        # -- Unused
        # self.exchange = 'NSE'
        # - For level 2 and level 3 data
        # self.bids = []
        # self.asks = []

    def __eq__(self, other):
        res = True
        assert type(self) == type(other)
        try:
            if self.tick_seq != other.tick_seq:
                res = False
            elif self.best_bid_price != other.best_bid_price\
                    or self.best_bid_qty != other.best_bid_qty\
                    or self.best_ask_price != other.best_ask_price\
                    or self.best_ask_qty != other.best_ask_qty:
                res = False
        except AttributeError:
            pass
        return res

    def __str__(self):
        if self.special_tag == "":
            starting_formatter = ending_formatter = ""
        else:
            if self.special_tag == "H":
                starting_formatter = f"{Style.BRIGHT}{Fore.GREEN}"
                ending_formatter = f"{Style.RESET_ALL}"
            elif self.special_tag == "L":
                starting_formatter = f"{Style.BRIGHT}{Fore.RED}"
                ending_formatter = f"{Style.RESET_ALL}"
            else:
                starting_formatter = ending_formatter = ""
        return f"{starting_formatter}{str(self.__dict__)}{ending_formatter}"

    def populate_using_touchline(self, touchline_data: TouchlineData):
        self.timestamp = datetime.now()
        self.symbol = touchline_data.symbol
        self.symbol_id = touchline_data.symbol_id
        self.day_high = touchline_data.high
        self.day_low = touchline_data.low
        self.day_open = touchline_data.open
        self.prev_day_close = touchline_data.prev_close
        self.prev_day_oi = touchline_data.prev_oi
        self.oi = touchline_data.oi
        self.ttq = touchline_data.ttq

        self.ltp = touchline_data.ltp
        self.calculate_additional_data()

    def calculate_additional_data(self):
        try:
            self.oi_change = self.oi - self.prev_day_oi
            self.oi_change_perc = self.oi_change * 100 / self.prev_day_oi
        except ZeroDivisionError:
            self.oi_change = self.oi_change_perc = 0
        except Exception as e:
            print(f"Encountered other oi calculation error: {e} with symbol {self.symbol} with tick_type={self.tick_type} and tick_seq={self.tick_seq}")
        try:
            self.change = self.ltp - self.prev_day_close
            self.change_perc = self.change * 100 / self.prev_day_close
        except ZeroDivisionError:
            self.change = self.change_perc = 0
        except Exception as e:
            print(f"Encountered other change calculation error: {e} with symbol {self.symbol} with tick_type={self.tick_type} and tick_seq={self.tick_seq}")


class MinLiveData:
    def __init__(self, symbol):
        # --Common Variables
        self.timestamp = None
        self.symbol = symbol
        self.symbol_id = None
        self.day_high = None
        self.day_low = None
        self.day_open = None
        self.prev_day_close = None
        self.prev_day_oi = None
        self.oi = None
        self.ttq = None
        # --Obj specific
        self.open = None
        self.high = None
        self.low = None
        self.close = None
        self.volume = None
        # -- Calculated common
        self.change = None
        self.change_perc = None
        self.oi_change = None
        self.oi_change_perc = None
        # -- Calculated specific
        # --Unused
        # self.exchange = 'NSE'
        # -For level 2 and level 3 data
        # self.bids = []
        # self.asks = []

    def __eq__(self, other):
        res = True
        assert type(self) == type(other)
        if self.timestamp != other.timestamp\
                or self.symbol != other.symbol:
            res = False
        return res

    def __str__(self):
        return str(self.__dict__)

    def populate_using_touchline(self, touchline_data: TouchlineData):
        self.timestamp = datetime.now()
        self.symbol = touchline_data.symbol
        self.symbol_id = touchline_data.symbol_id
        self.day_high = touchline_data.high
        self.day_low = touchline_data.low
        self.day_open = touchline_data.open
        self.prev_day_close = touchline_data.prev_close
        self.prev_day_oi = touchline_data.prev_oi
        self.oi = touchline_data.oi
        self.ttq = touchline_data.ttq

        self.close = touchline_data.ltp
        self.calculate_additional_data()

    def calculate_additional_data(self):
        try:
            self.oi_change = self.oi - self.prev_day_oi
            self.oi_change_perc = self.oi_change * 100 / self.prev_day_oi
        except ZeroDivisionError:
            self.oi_change = self.oi_change_perc = 0
        try:
            self.change = self.close - self.prev_day_close
            self.change_perc = self.change * 100 / self.prev_day_close
        except ZeroDivisionError:
            self.change = self.change_perc = 0
