import requests
from requests import RequestException
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os
import re


def get_from_to(date_from, date_to, code):
    url = f"https://www.mse.mk/mk/stats/symbolhistory/{code}"

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


def one_year_before(date):
    date_format = "%d.%m.%Y"
    given_date = datetime.strptime(date, date_format)
    one_year_ago = given_date.replace(year=given_date.year - 1)
    return one_year_ago.strftime(date_format)


def get_data_for(code):
    data_frame_list = []
    date_today = datetime.now().strftime("%d.%m.%Y")
    date_to = date_today
    date_from = one_year_before(date_to)
    for i in range(10):
        df = get_from_to(date_from, date_to, code)
        if df is None:
            continue
        data_frame_list.append(df)
        date_to = date_from
        date_from = one_year_before(date_to)
    return data_frame_list


def scrape_data(codes):
    output_dir = os.path.join(os.getcwd(), 'data')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for code in codes:
        df_list = get_data_for(code)
        result = df_list[0]
        for i in range(1, len(df_list)):
            result = pd.concat([result, df_list[i]], ignore_index=True)
        full_path = os.path.join(output_dir, f'{code}.csv')
        result.to_csv(full_path, index=False)


def get_codes():
    url = "https://www.mse.mk/mk/stats/symbolhistory/ADIN"
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


def main():
    codes = get_codes()
    scrape_data(codes)


if __name__ == "__main__":
    main()
