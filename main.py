#%%
import os
import csv
import datetime
import shutil
import requests
import re
from bs4 import BeautifulSoup
#%%
def get_exchange_rate():
    url = 'https://rate.bot.com.tw/xrt?Lang=zh-TW'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    currencies = soup.find_all('div', {'class': 'visible-phone print_hide'})
    buy_rates = soup.find_all('td', {'data-table': '本行現金買入'})
    sell_rates = soup.find_all('td', {'data-table': '本行現金賣出'})

    exchange_rates = {}
    for i in range(len(currencies)):
        currency = currencies[i].text.strip()
        buy_rate = buy_rates[i].text.replace('-', '0')
        sell_rate = sell_rates[i].text.replace('-', '0')
        exchange_rates[currency] = {'buy': buy_rate, 'sell': sell_rate}

    return exchange_rates
#%%
def create_csv_file(title,exchange_rates):
    date_time = datetime.datetime.now()
    month_year = date_time.strftime("%Y_%m")
    file_name = f"{month_year}.csv"
    file_path = os.path.join('data', file_name)
    if not os.path.exists('data'):
        os.makedirs('data')
    file_exists = os.path.isfile(file_path)
    with open(file_path, mode='a', newline='') as csv_file:
        fieldnames = title
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        write_row_data_list=[title,exchange_rates]
        write_row_data_list=list(map(list, zip(*write_row_data_list)))
        write_row_data = dict(write_row_data_list)
        writer.writerow(write_row_data)
    
    return file_path
#%%
def generate_title(title):
    re_value=[]
    for i in range(len(title)*2):
        if i%2==0:
            re_value.append(title[i//2]+'_buy')
        else:
            re_value.append(title[i//2]+'_sell')
    return re_value
#%%
def data_transfer(exchange_rates):
    currentDateAndTime = datetime.datetime.now()
    data=[]
    data.append(currentDateAndTime.year)
    data.append(currentDateAndTime.month)
    data.append(currentDateAndTime.day)
    data.append(currentDateAndTime.hour)
    data.append(currentDateAndTime.weekday())
    title=[re.search('\((.*?)\)',x).group(1) for x,y in exchange_rates.items()]
    title=['year','month','day','hour','weekday']+generate_title(title)
    
    for currency, rates in exchange_rates.items():
        data.append(rates['buy'])
        data.append(rates['sell'])
    return title,data

#%%
def delete_oldest_csv_file():
    total_size = sum(os.path.getsize(os.path.join('data', f)) for f in os.listdir('data') if os.path.isfile(os.path.join('data', f)))
    max_size = 500 * 1024 * 1024 # 500MB
    if total_size > max_size:
        files = sorted([f for f in os.listdir('data') if os.path.isfile(os.path.join('data', f))])
        for file in files:
            file_path = os.path.join('data', file)
            os.remove(file_path)
            total_size -= os.path.getsize(file_path)
            if total_size <= max_size:
                break
#%%
def main():
    exchange_rates = get_exchange_rate()
    title,exchange_rates_=data_transfer(exchange_rates)
    file_path = create_csv_file(title,exchange_rates_)
    delete_oldest_csv_file()
if __name__ == '__main__':
    main()
