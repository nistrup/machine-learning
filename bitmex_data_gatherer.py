import pandas as pd
import calendar
from time import sleep
import datetime
import sys

# Grundet at jeg lavede programmet som Python Notebook på Google Colab
from google.colab import drive
drive.mount('/content/drive/')
# Google Colab kode slut

binsize = "1m"
count_int = str(int((12 * 60) / 1))
symbol = "XBTUSD"
year_num = "2018"

def update_progress(progress):
    sys.stdout.write('\r[{0}{1}] {2}%'.format('#'*int(progress/2), '_'*(50-int(progress/2)), int(progress))),

def number_of_days_from_then_to_now(start_month, end_month):
    total_days = 0
    for month in range(start_month, end_month + 1):
        if month == now.month:
            total_days += now.day
    else:
        total_days += calendar.monthrange(2018, month)[1]
    return total_days

def time_format(start_hour, end_hour, day_num, month_num):
    start_time = f"{year_num}-{month_num}-{day_num}T{start_hour}%3A00%3A00.000Z"
    end_time = f"{year_num}-{month_num}-{day_num}T{end_hour}%3A00%3A00.000Z"
    return start_time, end_time

def get_dat_zero(input):
    output = str(input)
    if len(output) == 1:
        output = str("0" + output)
        return output
    else:
        return output

def get_daily_data(day_num, month_num):
    global main_df
    for half_of_day in range(0,2):
        if half_of_day == 0:
            start_time, end_time = time_format("00", "12", day_num, month_num)
            # print("Gathering " + symbol + "/BitMEX price-data from the " + day_num + "-" + month_num + "-" + year_num)
        if half_of_day == 1:
            start_time, end_time = time_format("12", "24", day_num, month_num)

            url = str(f"https://www.bitmex.com/api/v1/trade/bucketed?binSize={binsize}&partial=false&symbol={symbol}&count={count_int}&reverse=false&startTime={start_time}&endTime={end_time}")
            df = pd.read_json(url)
            df = df.rename(columns={'timestamp': 'time'})
            df.set_index('time', inplace=True)
            df = df[["close","volume"]]
            main_df = main_df.append(df)
            sleep(2)

def latest_bitmex_data(start_month)
    now = datetime.datetime.now()
    end_month = now.month

    for month in range(start_month, end_month + 1):

        progress = 0
        print("Gathering data from " + str(calendar.month_name[month]))
        days_in_month = calendar.monthrange(2018, month)[1]
        main_df = pd.DataFrame()

        if month == now.month:
            for day in range(1, now.day + 1):
                day_num = get_dat_zero(day)
                month_num = get_dat_zero(month)
                get_daily_data(day_num, month_num)
                progress += 100 / now.day
                update_progress(progress)

        else:
            for day in range(1, days_in_month + 1):
                day_num = get_dat_zero(day)
                month_num = get_dat_zero(month)
                get_daily_data(day_num, month_num)
                progress += 100 / days_in_month
                update_progress(progress)

        update_progress(100)
        print(" Done!")
        main_df.to_csv(f'/content/drive/My Drive/Machine Learning/crypto_data/{symbol}-{month_num}-{year_num}.csv')

latest_bitmex_data(1)