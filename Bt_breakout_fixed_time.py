import datetime as dt
import pandas as pd
from nsepy import get_history
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
from datetime import timedelta
import datetime

register_matplotlib_converters()
import ta as TA

start_date = dt.datetime(2016,10,1)
end_date = dt.datetime.today()
script_name = 'SBIN'

# get data from nsepy
df = pd.DataFrame(get_history(script_name, start=start_date, end=end_date, index=False))
# plot the closing prices
plt.plot(df['Close'])
# plt.show()
print(df.head(5))


# removing variables that are not needed
del df['Series'], df['Symbol'], df['Last'], df['Prev Close'], df['VWAP'], df['Volume'], df['Turnover'],df['Trades'], df['Deliverable Volume'],df['%Deliverble']
# df.to_excel('D:\Stock market\Backtesting\export.xlsx')
df.reset_index(level=0, inplace=True)
df.to_csv('D:\Stock market\Backtesting\export.csv')

'''
# Aggregating at a weekly level
print('*** Program Started ***')
# Converting date to pandas datetime format

weekday = dt.datetime.today().weekday()
df['Date'] = pd.to_datetime(df['Date'])
df['Week_Number'] = 0
date = 0
start_delta = datetime.timedelta(weeks=1)
for i in range(len(df['Close'])):
    date = df['Date'][i]
    df['Week_Number'][i] = (date - start_delta).isocalendar()[1]
    print(df['Week_Number'][i])


# Getting week number
# df['Week_Number'] = df['prev_week'].dt.isocalendar().week
# Getting year. Weeknum is common across years to we need to create unique index by using year and weeknum
df['Year'] = df['Date'].dt.year
# Grouping based on required values
# df2 = df.groupby(['Year', 'Week_Number']).agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last'})
'''



profit_target = .2  # change the value to test the results, set at 8%
stop_loss = .02  # change the value to test the results, set at 2%
buffer = .5
fast_period = 20  # fast moving SMA
slow_period = 50  # slow moving SMA
adx_limit = 35

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



# writing output to a file
f = open('D:/Stock market/Backtesting/Output1.csv', 'w')

for i in range(3,len(df['Close'])):
    last_price = df['Close'][i]
    # df['signal'][i] = 'none'
    High = max(df['High'][i-1],df['High'][i-2]) + buffer
    Low = min(df['Low'][i - 1], df['Low'][i - 2]) - buffer
    if position == 0 and df['High'][i] >= High:
        position = 1
        buy_count = buy_count + 1
        buy_val = High
        stop_loss_val = buy_val * (1-stop_loss)

        print(df['Date'][i], ";", "BUY-ENTRY;", buy_val, ";", profit,";", cum_profit)
        print(df['Date'][i], ";", "BUY-ENTRY;", buy_val, ";", profit,";", cum_profit, file=f)
    elif position == 0 and df['Low'][i] <= Low:
        position = -1
        sell_count = sell_count + 1
        sell_val = Low

        print(df['Date'][i], ";", "SELL-ENTRY;", sell_val, ";",profit,";", cum_profit)
        print(df['Date'][i], ";", "SELL-ENTRY;", sell_val, ";", profit,";",cum_profit, file=f)
    else:
        if position == 1 and df['Low'][i] < stop_loss_val:
            position = 0
            cum_profit = cum_profit + (stop_loss_val - buy_val)
            print(df['Date'][i], ";", "BUY-ENTRY;", buy_val, ";", profit, ";", cum_profit)
            print(df['Date'][i], ";", "BUY-ENTRY;", buy_val, ";", profit, ";", cum_profit, file=f)

        elif df['High'][i] >= High and position <= 0 :
            position = 1
            buy_count = buy_count + 1
            buy_val = High
            df.loc[df.index, 'signal'] = 'Buy-Entry'
            profit = (sell_val - buy_val)
            cum_profit = cum_profit + (sell_val - buy_val)
            print(df['Date'][i], ";", "BUY-ENTRY;", buy_val, ";",profit,";", cum_profit)
            print(df['Date'][i], ";", "BUY-ENTRY;", buy_val, ";", profit,";",cum_profit, file=f)
        elif df['Low'][i] < Low and position >= 0:
            position = -1
            sell_count = sell_count + 1
            sell_val = Low
            profit = (sell_val - buy_val)
            cum_profit = cum_profit + (sell_val - buy_val)
            df.loc[df.index, 'signal'] = 'SELL-Entry'
            print(df['Date'][i], ";", "SELL-ENTRY;", sell_val, ";", profit,";",cum_profit)
            print(df['Date'][i], ";", "SELL-ENTRY;", sell_val, ";", profit,";",cum_profit, file=f)
        else:
            continue



# print(df.tail())
print(script_name, ': Buys=', buy_count, 'Sells=', sell_count, "Profits=", cum_profit)

df.to_csv('D:\Stock market\Backtesting\export.csv')
df.to_excel('D:\Stock market\Backtesting\export.xlsx')
