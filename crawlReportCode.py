
import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://topi.vn/danh-sach-ma-chung-khoan-theo-nganh-tai-viet-nam.html"

response = requests.get(url)

soup = BeautifulSoup(response.content, "html.parser")

tables = soup.findAll("table")

data = []
for i, table in enumerate(tables):
    tbody = table.find("tbody")
    if not tbody:
        continue

    rows = tbody.find_all("tr")
    for row in rows[1:]:
        cols = row.find_all("td")
        row_data = [col.get_text(strip=True) for col in cols]
        if row_data:  #lấy dòng không rỗng
            data.append(row_data)

# print(data)



