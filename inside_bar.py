import datetime as dt
import pandas as pd
from nsepy import get_history
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
import datetime
import math


register_matplotlib_converters()
import ta as TA

# import data from csv file

df=pd.read_csv("D:\Stock market\Backtesting\BAJFINANCE15min.csv")    # replace with location of the file
#print(df.head())

# renaming the timestamp field to date
df.rename(columns={"timestamp": "date"}, inplace=True)
del df['oi']
# print(df.head())
# print(type(df.time))
# count number of rows
# print(df['close'].count)
max_price = df['close'].max()
# print(df.date[df.close == max_price])

# formatting the date and time variable
df['date'] = pd.to_datetime(df['date'], format="%d-%m-%Y", errors='coerce').dt.date
df['time'] = pd.to_datetime(df.time, format='%H:%M:%S', errors='coerce').dt.time

print("----breakout timeframe----")
# breakout parameter
range_start_time = datetime.time(9, 30, 0) # take first order after
range_end_time = datetime.time(14, 15, 0)  # entry before
day_end_time = datetime.time(15, 10, 0)  # the end of the trading session
print(range_start_time, range_end_time)

# for testing various target ranges, starting value, end value, and skip value

profit_multiplier = 1.5
max_SL = 30
max_TGT = 70

# variable assignment
position = 0
buy_val = 0
sell_val = 0
last_price = 0
profit = 0
cum_profit = 0

take_profit = 0
stop_loss_val = 0
buy_count = 0
sell_count = 0
trade_count = 0
loss = 0
win = 0
inside_bar = 0
SL_buy = 0
SL_sell = 0
diff = 0

df['signal'] = 'none'
# print(df.head())

ORB = {"high": 0, "low": 0}
# uncomment the print statements to get the trades for each day
for i in range(1, len(df['close'])):
    if df['date'][i] == df['date'][i-1]:   # check for same day
        if range_start_time <= df['time'][i] < day_end_time:    # check for range start
            # check for inside bar, mother candle > 75% body

            if inside_bar == 0 and df['high'][i] < df['high'][i-1] and df['low'][i] > df['low'][i-1] and (abs(df['open'][i-1]-df['close'][i-1]) > .75*abs(df['high'][i-1]-df['low'][i-1])):
            #if inside_bar == 0 and df['high'][i] < df['high'][i - 2] and df['low'][i] > df['low'][i - 2] and df['high'][i-1] < df['high'][i - 2] and df['low'][i-1] > df['low'][i - 2] and (
             #       abs(df['open'][i - 2] - df['close'][i - 2]) > .75 * abs(df['high'][i - 2] - df['low'][i - 2])):
                inside_bar = 1
                ORB['high'] = df['high'][i-1]
                SL_buy = df['low'][i]
                ORB['low'] = df['low'][i - 1]
                SL_sell = df['high'][i]
                diff = ORB['high'] - ORB['low']
                print(df['date'][i], df['time'][i], ORB['high'], ORB['low'])
            elif inside_bar == 1:
                if position == 0:
                    # buy entry
                    if df['high'][i] > ORB['high'] > df['low'][i] and (trade_count == 0 or trade_count == 4) and df['time'][i] < range_end_time:
                        trade_count += 2
                        position = 1
                        buy_val = ORB['high']
                        buy_count = buy_count + 1
                        stop_loss_val = buy_val - min(max_SL, diff)
                        take_profit = buy_val + profit_multiplier * diff
                        print(df['date'][i], df['time'][i], "Buy@", buy_val, "tgt", take_profit, "SL", stop_loss_val)
                    # sell entry
                    elif df['low'][i] < ORB['low'] < df['high'][i] and (trade_count == 0 or trade_count == 2) and df['time'][i] < range_end_time:
                        trade_count += 4
                        position = -1
                        sell_val = ORB['low']
                        sell_count = sell_count + 1
                        stop_loss_val = sell_val + min(max_SL, diff)
                        take_profit = sell_val - profit_multiplier * diff
                        print(df['date'][i], df['time'][i], "Sell@", sell_val, "tgt", take_profit, "SL", stop_loss_val)
                elif position != 0:
                    # buy exit- profit or sl
                    if df['high'][i] >= take_profit and position == 1:

                        position = 0
                        profit = take_profit - buy_val
                        cum_profit = cum_profit + profit
                        print(df['date'][i], df['time'][i], "Buy_TP@", take_profit, "profit", cum_profit, "result", profit)
                        win = win + 1
                    elif df['low'][i] < stop_loss_val and position == 1:

                        position = 0
                        profit = buy_val - stop_loss_val
                        cum_profit = cum_profit - profit
                        print(df['date'][i], df['time'][i], "buy_SL@", stop_loss_val, "profit", cum_profit, "result", -profit)
                        loss = loss + 1
                        # sell exit, either profit or loss
                    elif df['low'][i] < take_profit and position == -1:

                        position = 0
                        profit = sell_val - take_profit
                        cum_profit = cum_profit + profit
                        print(df['date'][i], df['time'][i], "sell_TP@", take_profit, "profit", cum_profit, "result", profit)
                        win = win + 1
                    elif df['high'][i] > stop_loss_val and position == -1:

                        position = 0
                        profit = stop_loss_val - sell_val
                        cum_profit = cum_profit - profit
                        print(df['date'][i], df['time'][i], "sell_SL@", stop_loss_val, "profit", cum_profit, "result", -profit)
                        loss = loss + 1
                    # day end, no profit/SL, exit at 3.10PM
                    elif df['time'][i].hour == 15 and df['time'][i].minute == 0 and position != 0:
                        if position == 1:

                            position = 0
                            profit = df['close'][i] - buy_val
                            cum_profit = cum_profit + profit
                            print(df['date'][i], df['time'][i], "Buy_exit@", df['close'][i], "profit", cum_profit, "result", profit)
                        elif position == -1:

                            position = 0
                            profit = (sell_val - df['close'][i])
                            cum_profit = cum_profit + profit
                            print(df['date'][i], df['time'][i], "sell_exit@", df['close'][i],"profit", cum_profit, "result", profit)
                        if profit > 0:
                            win = win + 1
                        else:
                            loss = loss + 1

        else:
            inside_bar = 0
            position = 0
            trade_count = 0


print("trades=", buy_count + sell_count, "win%", round(win / (win + loss), 2), "profit=", round(cum_profit))
'''
def buy_entry(date, time, high_current_candle, low_current_candle, entry_price, candle_length, trade_count, position):
    print("buy entry @",date + time )
    if high_current_candle>entry_price>low_current_candle and trade_count == (0 or 4):
        buy_val =
'''