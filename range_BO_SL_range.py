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
df=pd.read_csv("D:\Stock market\Backtesting\BAJFINANCE.csv")
#print(df.head())

# renaming the timestamp field to date
df.rename(columns={"timestamp" : "date"}, inplace=True)
del df['oi']
# print(df.head())
# print(type(df.time))
# count number of rows
# print(df['close'].count)
max_price = df['close'].max()
# print(df.date[df.close == max_price])

# breakout parameter
range_start_time = datetime.time(9,15,0)
range_end_time = datetime.time(10,5,0)

SL = 0
TGT = 0
early_entry = 10
double_side_BO = 0
max_loss = 10000
RR_ratio = 2

# variable assignment
position = 0
buy_val = 0
sell_val = 0
last_price = 0
profit = 0
cum_profit = 0
qty = 0

take_profit = 0
stop_loss_val = 0
buy_count = 0
sell_count = 0
trade_count = 0
range_diff = 0

df['signal'] = 'none'
print(df.head())

# formatting the date and time variable
df['date'] = pd.to_datetime(df['date'], format="%d-%m-%Y", errors='coerce').dt.date
df['time'] = pd.to_datetime(df.time, format='%H:%M:%S', errors='coerce').dt.time

ORB = {"high": 0, "low": 999999}
print(ORB['high'])


for i in range(1, len(df['close'])):

    if (df['date'][i] == df['date'][i-1]):
        if df['time'][i].hour < range_end_time.hour or (df['time'][i].hour == range_end_time.hour and df['time'][i].minute < range_end_time.minute):
            #check rounding based on stock price

            ORB['high'] = round(max(ORB['high'], df['high'][i]), 0)
            ORB['low'] = round(min(ORB['low'], df['low'][i]), 0)
            range_diff = ORB['high'] - ORB['low']
            # print(df['time'][i], df['high'][i], df['low'][i], ORB['high'], ORB['low'])
            # print(df['date'][i], high, low)
        elif df['time'][i].hour <= 15 or (df['time'][i].hour == 15 and df['time'][i].minute >5):
            if df['high'][i] > (ORB['high'] - early_entry) and position == 0 and (trade_count == 0 or trade_count == 4*double_side_BO):
                position = 1
                trade_count = trade_count + 2
                buy_val = ORB['high'] - early_entry
                buy_count = buy_count+1
                TGT = (RR_ratio * range_diff)
                SL = range_diff
                take_profit = buy_val + TGT
                stop_loss_val = buy_val - SL
                qty = math.floor(max_loss / range_diff)

                print(df['date'][i], df['time'][i], "Buy@", buy_val, "TGT", take_profit, "SL", SL)

            #sell entry
            elif df['low'][i] < (ORB['low'] + early_entry) and position == 0 and (trade_count == 0 or trade_count == 2*double_side_BO):
                position = -1
                trade_count = trade_count + 4
                sell_val = ORB['low'] + early_entry
                sell_count = buy_count + 1
                TGT = (RR_ratio * range_diff)
                SL = range_diff
                take_profit = sell_val - TGT
                stop_loss_val = sell_val + SL
                qty = math.floor(max_loss / range_diff)
                print(df['date'][i], df['time'][i], "sell@", sell_val, "TGT", take_profit, "SL", SL)

            # buy exit, either profit or loss
            elif df['high'][i] > take_profit and position == 1:
                position = 0
                profit = (TGT * qty)
                cum_profit = cum_profit + profit
                print(df['date'][i], df['time'][i], "Buy_TP@", take_profit, "trade_profit", profit, "profit", cum_profit)

            elif df['low'][i] < stop_loss_val and position == 1:
                position = 0
                profit = (SL * qty)
                cum_profit = cum_profit - profit
                print(df['date'][i], df['time'][i], "Buy_SL@", stop_loss_val, "trade_profit", -profit, "profit", cum_profit)

                # sell exit, either profit or loss
            elif df['low'][i] < take_profit and position == -1:

                position = 0
                profit = (TGT * qty)
                cum_profit = cum_profit + profit
                print(df['date'][i], df['time'][i], "SL_TP@", take_profit, "trade_profit", profit, "profit", cum_profit)

            elif df['high'][i] > stop_loss_val and position == -1:
                position = 0
                profit = (SL * qty)
                cum_profit = cum_profit - profit
                print(df['date'][i], df['time'][i], "Sell_SL@", stop_loss_val, "trade_profit", -profit, "profit", cum_profit)

            #day end, no profit/SL, exit at 3.10PM
            elif df['time'][i].hour == 15 and df['time'][i].minute == 5 and position != 0:
                trade_count = trade_count + 1
                if position == 1:
                    position = 0
                    profit = (df['close'][i] - buy_val) * qty
                    cum_profit = cum_profit + profit
                    print(df['date'][i], df['time'][i], "Buy_exit@", df['close'][i], "trade_profit", profit, "profit", cum_profit)
                elif position == -1:
                    position = 0
                    profit = (sell_val - df['close'][i]) * qty
                    cum_profit = cum_profit + profit
                    print(df['date'][i], df['time'][i], "sell_exit@", df['close'][i], "trade_profit", profit, "profit", cum_profit)

    else:
        ORB['high'] = 0
        ORB['low'] = 99999
        position = 0
        trade_count = 0
        qty = 0
        TGT = 0
        SL = 0

print("trades=", buy_count+sell_count, "profit=",cum_profit)



