
import requests
import pandas as pd
from bs4 import BeautifulSoup

import os

url = "https://topi.vn/danh-sach-ma-chung-khoan-theo-nganh-tai-viet-nam.html"

response = requests.get(url)

soup = BeautifulSoup(response.content, "html.parser")

h3s = soup.findAll("h3")

folder_path = r'/CrawlFinanceReport/ReportFinance/ReportCode'
os.makedirs(folder_path, exist_ok=True)

for h3 in h3s:
    strong = h3.find("strong")
    if not strong:
        continue

    nameStockGroup = strong.get_text(strip=True)
    print(nameStockGroup)

    tables = h3.find_next("table")

    data = []

    for i, table in enumerate(tables):
        if not table:
            continue

        rows = table.find_all("tr")

        if not rows or len(rows) < 2:
            continue

        header = [col.get_text(strip=True) for col in rows[0].find_all("td")]

        for row in rows[1:]:
            cols = row.find_all("td")
            row_data = [col.get_text(strip=True) for col in cols]
            if row_data:
                data.append(row_data)

        df = pd.DataFrame(data, columns=header)
        print(df)

        name_df = nameStockGroup[2:]
        csv_path = os.path.join(folder_path,f"{name_df}.csv")
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
