import requests
from requests import RequestException
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import os
import re
from tqdm import tqdm


# gets the code of all valid publishers and returns them as a list of strings
def get_codes():
    url = "https://www.mse.mk/en/stats/symbolhistory/ADIN"
    response = requests.get(url)
    if response.status_code != 200:
        print("Bad response code")
        return None
    soup = BeautifulSoup(response.text, "html.parser")
    select_tag = soup.find('select', id='Code')
    codes = []
    for option in select_tag.find_all('option'):
        if 'value' in option.attrs:
            codes.append(option['value'])

    codes_without_digits = []
    for s in codes:
        if not re.search(r'\d', s):
            codes_without_digits.append(s)

    bonds = ["TTK", "TTKO", "CKB", "CKBKO", "SNBT", "SNBTO"]
    filtered_codes = []
    for item in codes_without_digits:
        if item not in bonds:
            filtered_codes.append(item)
    return filtered_codes


# checks the last retrieved date in CSV files for each publisher and returns a map where key is the code and value is latest date
def get_latest_date(codes):
    result = {}
    path = os.path.join(os.getcwd(), "data")

    for code in codes:
        file_path = os.path.join(path, f"{code}.csv")
        if not os.path.exists(file_path):
            result[code] = None
            continue

        df = pd.read_csv(file_path)

        if df.empty:
            result[code] = None
            continue

        df['Date'] = pd.to_datetime(df['Date'], format='%d.%m.%Y', errors='coerce')
        latest_date = df['Date'].max()
        result[code] = latest_date.strftime('%d.%m.%Y')
    return result


# handles data scraping for that code from date_from to date_to
def get_from_to(code, date_from, date_to):
    url = f"https://www.mse.mk/en/stats/symbolhistory/{code}"

    payload = f"FromDate={date_from}&ToDate={date_to}&Code={code}"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = None
    try:
        response = requests.post(url, data=payload, headers=headers)
        response.raise_for_status()
    except RequestException as e:
        print(f"An error occurred: {e}")
    if response is None:
        return None
    if response.status_code != 200:
        print("Bad response code")
        return None
    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table", id="resultsTable")

    if table is None:
        return None

    rows_data = []
    header_row = table.find("tr")
    headers = [th.text.strip() for th in header_row.find_all("th")]

    for row in table.find_all("tr")[1:]:
        row_data = [td.text.strip() for td in row.find_all("td")]
        rows_data.append(row_data)

    return pd.DataFrame(rows_data, columns=headers)


# gets a date and a number representing years and returns a date plus the number of years passed to it
def adjust_year(date, years):
    date_format = "%m/%d/%Y"
    date_obj = datetime.strptime(date, date_format)
    adjusted_date = date_obj.replace(year=date_obj.year + years)
    return adjusted_date.strftime(date_format)


# returns a list of DataFrame objects from the date passed in(+1 day) up to the current date
def get_recent(code, date):
    date_obj = datetime.strptime(date, "%d.%m.%Y")
    formatted_date = date_obj.strftime("%m/%d/%Y")
    date_from = (datetime.strptime(formatted_date, "%m/%d/%Y") + timedelta(days=1)).strftime("%m/%d/%Y")
    data_frame_list = []
    do_loop = True
    while do_loop:
        date_to = adjust_year(date_from, 1)
        if datetime.strptime(date_to, "%m/%d/%Y") > datetime.now():
            date_to = datetime.now().strftime("%m/%d/%Y")
            do_loop = False

        df = get_from_to(code, date_from, date_to)
        if df is not None:
            data_frame_list.append(df)
        date_from = date_to

    return data_frame_list


# gets last 10 years of data for that code and returns a list of Data Frames
def get_last_ten_years(code):
    data_frame_list = []
    date_to = datetime.now().strftime("%m/%d/%Y")
    for i in range(10):
        date_from = adjust_year(date_to, -1)

        df = get_from_to(code, date_from, date_to)
        if df is None:
            continue

        data_frame_list.append(df)
        date_to = date_from

    return data_frame_list


# scrapes data for each publisher and returns a map where key is code and value is a Data Frame
def scrape_data(last_date_map):
    data = {}
    for code, date in tqdm(last_date_map.items(), ncols=100, colour='green'):
        if date is None:
            df_list = get_last_ten_years(code)
        else:
            df_list = get_recent(code, date)
        if len(df_list) == 0:
            data[code] = None
            continue
        result = df_list[0]
        for i in range(1, len(df_list)):
            result = pd.concat([result, df_list[i]], ignore_index=True)
        result['Date'] = pd.to_datetime(result['Date'], format='%m/%d/%Y')
        result['Date'] = result['Date'].dt.strftime('%d.%m.%Y')
        data[code] = result

    return data


# saves csv files in folder called data
def save(data):
    output_dir = os.path.join(os.getcwd(), 'data')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for code, df in data.items():
        if data[code] is None:
            continue
        full_path = os.path.join(output_dir, f'{code}.csv')
        df.to_csv(full_path, mode='a', index=False, header=False)


def main():
    codes = get_codes()
    latest_date_map = get_latest_date(codes)
    data = scrape_data(latest_date_map)
    save(data)


if __name__ == "__main__":
    main()
