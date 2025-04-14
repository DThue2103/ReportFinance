
import requests
import pandas as pd
from pandas.core.interchange.dataframe_protocol import DataFrame
from bs4 import BeautifulSoup

df = pd.read_csv("/CrawlFinanceReport/ReportFinance/ReportCode\ Nhóm cổ phiếu ngành ngân hàng.csv")

for i, row in df.iterrows():
    reportCode = row.iloc[1]
    url = f"https://cafef.vn/du-lieu/hose/{reportCode}.chn"
    # print(url)

    response = requests.get(url)

    soup = BeautifulSoup(response.content, "html.parser")

    h2s = soup.findAll("h2")

    for h2 in h2s:
        content_h2 = h2.get_text(strip=True)
        if content_h2 == "TÌNH HÌNH TÀI CHÍNH VÀ CÔNG TY CON":
            li = h2.find_next('li')

