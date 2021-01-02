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
range_start_time = datetime.time(9,0,0)
range_end_time = datetime.time(10,5,0)
day_end_time = datetime.time(15,5,0)

SL = 40       # min SL irrespective of the range
TGT = 0
early_entry = 10    # number of point to enter before the range breakout
double_side_BO = 0   # 1= both sides, 0=single side
max_loss = 5000  # for fixed loss
RR_ratio = 1   # change for higher or lower risk reward ratio
fixed_SL = 0     # if every trade has fixed SL, else make it 0 to keep range based SL

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
win = 0
loss = 0
trade_entry_time = datetime.time(0,0,0)

df['signal'] = 'none'
# print(df.head())

# formatting the date and time variable
df['date'] = pd.to_datetime(df['date'], format="%d-%m-%Y", errors='coerce').dt.date
df['time'] = pd.to_datetime(df.time, format='%H:%M:%S', errors='coerce').dt.time

ORB = {"high": 0, "low": 999999}
# print(ORB['high'])


for i in range(1, len(df['close'])):
    #new day
    if df['date'][i] != df['date'][i-1]:
        # print(df['date'][i], round(cum_profit))
        #print(df['date'][i-1],ORB['high'], ORB['low'])
        ORB['high'] = df['high'][i]
        ORB['low'] = df['low'][i]
        #print(df['date'][i], ORB['high'], ORB['low'])
        position = 0
        trade_count = 0
        qty = 0
        TGT = 0

    # range calculation
    elif df['date'][i] == df['date'][i-1] and df['time'][i].hour < range_end_time.hour or (df['time'][i].hour == range_end_time.hour and df['time'][i].minute <= range_end_time.minute):
        #check rounding based on stock price
        ORB['high'] = round(max(ORB['high'], df['high'][i]))
        ORB['low'] = round(min(ORB['low'], df['low'][i]))
        if fixed_SL == 1:
            range_diff = SL
        else:
            range_diff = max(ORB['high'] - ORB['low'], SL)


    elif df['time'][i].hour <= day_end_time.hour or (df['time'][i].hour == 15 and df['time'][i].minute == day_end_time.minute):
        if df['high'][i] > (ORB['high'] - early_entry) > df['low'][i] and position == 0 and (trade_count == 0 or trade_count == 4*double_side_BO):
            position = 1
            trade_count = trade_count + 2
            buy_val = ORB['high'] - early_entry
            buy_count = buy_count+1
            TGT = (RR_ratio * range_diff)

            take_profit = round(buy_val + TGT)
            stop_loss_val = round(buy_val - range_diff)
            qty = math.floor(max_loss / range_diff)
            #print(df['date'][i], ORB['high'], ORB['low'])
            #print(df['date'][i], df['time'][i], "Buy@", buy_val, "TGT", take_profit, "SL", stop_loss_val)

        #sell entry
        elif df['low'][i] < (ORB['low'] + early_entry) <df['high'][i] and position == 0 and (trade_count == 0 or trade_count == 2*double_side_BO):
            trade_entry_time = df['time'][i]
            position = -1
            trade_count = trade_count + 4
            sell_val = ORB['low'] + early_entry
            sell_count = buy_count + 1
            TGT = (RR_ratio * range_diff)
            take_profit = round(sell_val - TGT)
            stop_loss_val = round(sell_val + range_diff)
            qty = math.floor(max_loss / range_diff)
            # print(df['date'][i], ORB['high'], ORB['low'])
            # print(df['date'][i], df['time'][i], "sell@", sell_val, "TGT", take_profit, "SL", stop_loss_val)


        # buy exit, either profit or loss
        elif df['high'][i] > take_profit and position == 1:
            position = 0
            profit = (TGT * qty)
            cum_profit = cum_profit + profit
            win += 1
            print(df['date'][i], "entry", trade_entry_time,"entry_price", buy_val,stop_loss_val,take_profit, "exit", df['time'][i],"exit_price", take_profit,"Result", profit, "result_type", "BUY-TP")

        elif df['low'][i] < stop_loss_val and position == 1:
            position = 0
            profit = (range_diff * qty)
            cum_profit = cum_profit - profit
            loss += 1
            print(df['date'][i], "entry", trade_entry_time,"entry_price", buy_val,stop_loss_val,take_profit, "exit", df['time'][i],"exit_price", stop_loss_val,"Result", -profit, "result_type", "BUY-SL")

            # sell if double side entry
            if df['low'][i] < (ORB['low'] + early_entry) < df['high'][i] and position == 0 and (
                        trade_count == 0 or trade_count == 2 * double_side_BO):
                position = -1
                trade_count = trade_count + 4
                sell_val = ORB['low'] + early_entry
                sell_count = buy_count + 1
                TGT = (RR_ratio * range_diff)

                take_profit = round(sell_val - TGT)
                stop_loss_val = round(sell_val + range_diff)
                qty = math.floor(max_loss / range_diff)
                #print(df['date'][i], ORB['high'], ORB['low'])
                #print(df['date'][i], df['time'][i], "sell@", sell_val, "TGT", take_profit, "SL", stop_loss_val)

            # sell exit, either profit or loss
        elif df['low'][i] < take_profit and position == -1:

            position = 0
            profit = (TGT * qty)
            cum_profit = cum_profit + profit
            win += 1
            print(df['date'][i], "entry", trade_entry_time,"entry_price", sell_val,stop_loss_val,take_profit, "exit", df['time'][i],"exit_price", take_profit,"Result", profit, "result_type", "SELL-TP")


        elif df['high'][i] > stop_loss_val and position == -1:
            position = 0
            profit = (range_diff * qty)
            cum_profit = cum_profit - profit
            loss = loss + 1
            print(df['date'][i], "entry", trade_entry_time,"entry_price", sell_val,stop_loss_val,take_profit, "exit", df['time'][i],"exit_price", stop_loss_val,"Result", -profit, "result_type", "SEll-SL")

            # buy if double side entry
            if df['high'][i] > (ORB['high'] - early_entry) > df['low'][i] and position == 0 and (
                    trade_count == 0 or trade_count == 4 * double_side_BO):
                position = 1
                trade_count = trade_count + 2
                buy_val = ORB['high'] - early_entry
                buy_count = buy_count + 1
                TGT = (RR_ratio * range_diff)

                take_profit = round(buy_val + TGT)
                stop_loss_val = round(buy_val - range_diff)
                qty = math.floor(max_loss / range_diff)
                #print(df['date'][i], ORB['high'], ORB['low'])
                # print(df['date'][i], df['time'][i], "sell@", sell_val, "TGT", take_profit, "SL", stop_loss_val)


        #day end, no profit/SL, exit at 3.10PM
        elif df['time'][i].hour == day_end_time.hour and df['time'][i].minute == day_end_time.minute and position != 0:
            trade_count = trade_count + 1
            if position == 1:
                position = 0
                profit = round((df['close'][i] - buy_val) * qty)
                cum_profit = cum_profit + profit
                print(df['date'][i], "entry", trade_entry_time,"entry_price", buy_val,stop_loss_val, take_profit, "exit", df['time'][i],"exit_price", round(df['close'][i]), "Result", profit, "result_type", "BUY-exit")
                if profit >= 0:
                    win = win + 1
                else:
                    loss = loss + 1
            elif position == -1:
                position = 0
                profit = round((sell_val - df['close'][i]) * qty)
                cum_profit = cum_profit + profit
                print(df['date'][i], "entry", trade_entry_time,"entry_price", sell_val, stop_loss_val, take_profit, "exit", df['time'][i],"exit_price", round(df['close'][i]), "Result", profit, "result_type", "SELL-exit")
                if profit >= 0:
                    win = win + 1
                else:
                    loss = loss + 1


print("trades=", win+loss, "win",  win, "loss", loss, "win%", win/(win + loss), "profit=",cum_profit)



