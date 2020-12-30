import datetime as dt
import pandas as pd
from nsepy import get_history
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
import datetime


register_matplotlib_converters()
import ta as TA

# import data from csv file

df=pd.read_csv("D:\Stock market\Backtesting\BAJFINANCE.csv")    # replace with location of the file
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
range_start_time = datetime.time(9, 15, 0)
range_end_time = datetime.time(10, 5, 0)
day_end_time = datetime.time(15, 10, 0)  # the end of the trading session
print(range_start_time, range_end_time)

# for testing various target ranges, starting value, end value, and skip value
for j in range(30, 150, 20):

    SL = 20       # change the SL
    TGT = j
    early_entry = 10 # early entry
    double_side_BO = 1 # make it 0 in case you want single side breakout

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

    df['signal'] = 'none'
    # print(df.head())

    ORB = {"high": 0, "low": 999999}
    # uncomment the print statements to get the trades for each day
    for i in range(1, len(df['close'])):

        if df['date'][i] == df['date'][i-1]:   # check for same day
            if range_start_time <= df['time'][i] < day_end_time:    # check for range start
                if df['time'][i] < range_end_time:     # check for range end
                    ORB['high'] = round(max(ORB['high'], df['high'][i]), 0)
                    ORB['low'] = round(min(ORB['low'], df['low'][i]), 0)
                    # print(df['date'][i], df['time'][i], df['high'][i], df['low'][i], ORB['high'], ORB['low'])
                # buy entry
                elif df['high'][i] > (ORB['high'] - early_entry) and position == 0 and (trade_count == 0 or trade_count == 4*double_side_BO) and (df['time'][i].hour < day_end_time.hour):
                    position = 1
                    trade_count = trade_count + 2
                    buy_val = ORB['high'] - early_entry
                    buy_count = buy_count+1
                    take_profit = buy_val + TGT
                    stop_loss_val = buy_val - SL
                    # print(df['date'][i], df['time'][i], "Buy@", buy_val, "profit", cum_profit)

                #sell entry
                elif df['low'][i] < (ORB['low'] + early_entry) and position == 0 and (trade_count == 0 or trade_count == 2*double_side_BO) and (df['time'][i].hour < day_end_time.hour):
                    position = -1
                    trade_count = trade_count + 4
                    sell_val = ORB['low'] + early_entry
                    sell_count = buy_count + 1
                    take_profit = sell_val - TGT
                    stop_loss_val = sell_val + SL
                    # print(df['date'][i], df['time'][i], "sell@", sell_val, "profit", cum_profit)

                # buy exit, either profit or loss
                elif df['high'][i] > take_profit and position == 1:
                    position = 0
                    profit = TGT
                    cum_profit = cum_profit + profit
                    # print(df['date'][i], df['time'][i], "Buy_TP@", take_profit, "profit", cum_profit, "result", profit)
                    win = win + 1

                elif df['low'][i] < stop_loss_val and position == 1:
                    position = 0
                    profit = SL
                    cum_profit = cum_profit - SL
                    # print(df['date'][i], df['time'][i], "buy_SL@", stop_loss_val, "profit", cum_profit, "result", -profit)
                    loss = loss + 1

                    # sell exit, either profit or loss
                elif df['low'][i] < take_profit and position == -1:

                    position = 0
                    profit = TGT
                    cum_profit = cum_profit + profit
                    # print(df['date'][i], df['time'][i], "sell_TP@", take_profit, "profit", cum_profit, "result", profit)
                    win = win + 1

                elif df['high'][i] > stop_loss_val and position == -1:
                    position = 0
                    profit = SL
                    cum_profit = cum_profit - SL
                    # print(df['date'][i], df['time'][i], "sell_SL@", stop_loss_val, "profit", cum_profit, "result", -profit)
                    loss = loss + 1

                #day end, no profit/SL, exit at 3.10PM
                elif df['time'][i].hour == 15 and df['time'][i].minute == 5 and position != 0:
                    trade_count = trade_count + 1
                    if position == 1:
                        position = 0
                        profit = df['close'][i] - buy_val
                        cum_profit = cum_profit + profit
                        # print(df['date'][i], df['time'][i], "Buy_exit@", df['close'][i], "profit", cum_profit, "result", profit)
                    elif position == -1:
                        position = 0
                        profit = (sell_val - df['close'][i])
                        cum_profit = cum_profit + profit
                        # print(df['date'][i], df['time'][i], "sell_exit@", df['close'][i],"profit", cum_profit, "result", profit)
                    if profit > 0:
                        win = win + 1
                    else:
                        loss = loss + 1

        else:
            ORB['high'] = 0
            ORB['low'] = 99999
            position = 0
            trade_count = 0

    print("TGT:Sl:Entry=", TGT, ":", SL, ":", early_entry, ",trades=", buy_count+sell_count, "win%", round(win/(win+loss), 2), "profit=", round(cum_profit))



