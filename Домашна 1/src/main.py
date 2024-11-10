import requests
from requests import RequestException
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import os
import re
from tqdm import tqdm
import sqlite3


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


# checks the db and retrives the latest date for each publisher and returns a map where key is the code and value is latest date
def get_latest_date(codes, db_file_path):
    result = {}
    current_date = datetime.now()

    if not os.path.exists(db_file_path):
        open(db_file_path, 'w').close()

    try:
        conn = sqlite3.connect(db_file_path)
        cursor = conn.cursor()

        for code in codes:
            result[code] = None

            try:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (code,))
                table_exists = cursor.fetchone()

                if not table_exists:
                    cursor.execute(f"CREATE TABLE IF NOT EXISTS {code} (Date TEXT)")
                    conn.commit()
                    result[code] = None
                    continue

                cursor.execute(f"SELECT Date FROM {code}")
                dates = [row[0] for row in cursor.fetchall()]
                if len(dates) == 0:
                    result[code] = None
                    continue

                date_objects = [datetime.strptime(date_str, "%d.%m.%Y") for date_str in dates]
                most_recent_date = max((date for date in date_objects if date <= current_date), default=None)
                result[code] = most_recent_date.strftime("%d.%m.%Y") if most_recent_date else None

            except sqlite3.Error:
                result[code] = None

    except sqlite3.OperationalError as e:
        print(f"Database error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

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
        result = result[result["Total turnover in denars"] != "0"]

        date = pd.to_datetime(result['Date'])
        result.loc[:, 'Date'] = date.dt.strftime('%d.%m.%Y')

        result = result.replace('', '0')
        data[code] = result
    return data


# saves data to database with that path
def save(data, db_file_path):
    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()

    for code, df in data.items():
        if df is None:
            continue
        field_names = []
        for col in df.columns:
            field_names.append(col.replace(' ', '_').replace(',', '').replace('.', '').replace('%', ''))

        column_definitions = []
        for col in field_names:
            if col == 'Date':
                column_definitions.append(f"{col} TEXT")
                continue
            column_definitions.append(f"{col} REAL")

        create_table_sql = f"CREATE TABLE IF NOT EXISTS {code} ({', '.join(column_definitions)});"
        cursor.execute(create_table_sql)

        for index, row in df.iterrows():
            values = [row['Date']]

            values[0] = f"'{values[0]}'"

            for col in df.columns:
                if col != 'Date':
                    cleaned_value = str(row[col]).replace(',', '')
                    numeric_value = pd.to_numeric(cleaned_value, errors='coerce')
                    values.append(numeric_value)

            insert_sql = f"INSERT INTO {code} ({', '.join(field_names)}) VALUES ({', '.join(map(str, values))})"
            cursor.execute(insert_sql)

    conn.commit()
    conn.close()


def main():
    output_dir = os.path.join(os.getcwd(), 'data')
    file_name = 'database.sqlite'
    db_file_path = os.path.join(output_dir, file_name)

    codes = get_codes()
    latest_date_map = get_latest_date(codes, db_file_path)
    data = scrape_data(latest_date_map)
    save(data, db_file_path)


if __name__ == "__main__":
    main()
