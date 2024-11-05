import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os


def collect_data(output_directory='data', output_filename='data.csv'):
    cwd = os.getcwd()
    os.makedirs(output_directory, exist_ok=True)
    csv_files = [file for file in os.listdir(cwd) if file.endswith('.csv')]
    combined_df = pd.DataFrame()
    for csv_file in csv_files:
        file_path = os.path.join(cwd, csv_file)
        df = pd.read_csv(file_path)
        combined_df = pd.concat([combined_df, df], ignore_index=True)

    output_path = os.path.join(output_directory, output_filename)
    combined_df.to_csv(output_path, index=False)
    for file in csv_files:
        os.remove(os.path.join(cwd, file))
    print(f"Combined data saved to {output_path}")


def one_year_before(input_date):
    date_format = "%d.%m.%Y"
    given_date = datetime.strptime(input_date, date_format)
    one_year_ago = given_date.replace(year=given_date.year - 1)
    return one_year_ago.strftime(date_format)


def get_from_to(date_from, date_to):
    url = "https://www.mse.mk/mk/stats/symbolhistory/REPL"

    payload = f"FromDate={date_from}&ToDate={date_to}&Code=REPL"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    response = requests.post(url, data=payload, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        table = soup.find("table", id="resultsTable")

        rows_data = []
        headers = []

        if table:
            header_row = table.find("tr")
            headers = [th.text.strip() for th in header_row.find_all("th")]

            # Extract each row's data
            for row in table.find_all("tr")[1:]:  # Skip header row
                row_data = [td.text.strip() for td in row.find_all("td")]
                rows_data.append(row_data)

            row_count = len(rows_data)
            print(f"Number of data rows: {row_count}")

            df = pd.DataFrame(rows_data, columns=headers)
            df.to_csv(f"{date_from}-{date_to}.csv", index=False)
            print("Data saved to resultsTable.csv")
        else:
            print("Table with id 'resultsTable' not found.")
    else:
        print("Failed to retrieve the data. Status code:", response.status_code)


def scrape_data():
    date_to = datetime.now().strftime("%d.%m.%Y")
    date_from = one_year_before(date_to)
    get_from_to(date_from, date_to)
    for i in range(10):
        get_from_to(date_from, date_to)
        date_to = date_from
        date_from = one_year_before(date_to)


def main():
    scrape_data()
    collect_data()


if __name__ == "__main__":
    main()