
import requests
import pandas as pd
from pandas.core.interchange.dataframe_protocol import DataFrame
from bs4 import BeautifulSoup
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import os

def get_report_pdf_link(reportCode):
    # truy cập vào trang web thông tin trên cafef của từng công ty
    url = f"https://cafef.vn/du-lieu/hose/{reportCode}.chn"
    # print(url)

    chrome_options = Options()
    chrome_options.add_argument("--headless")

    # 1. Tạo service object, trỏ đến đường dẫn chromedriver
    driver_path = ChromeDriverManager().install()
    service = Service(driver_path)

    # 2. Khởi tạo trình duyệt
    browser = webdriver.Chrome(service=service, options=chrome_options)

    # 3. Mở trang web
    browser.get(url)

    # Kiểm tra xem có nút "Tải BCTC" hay không và nhấn vào
    try:
        wait = WebDriverWait(browser, 20)
        wait.until(EC.presence_of_element_located((By.ID, "lsTab5CT")))
        wait.until(EC.visibility_of_element_located((By.ID, "lsTab5CT")))
        button = wait.until(EC.element_to_be_clickable((By.ID, "lsTab5CT")))
        browser.execute_script("arguments[0].click();", button)
        # button.click()
        print(f"Đã click vào nút Tải BCTC của {reportCode}")
        sleep(5)
    except NoSuchElementException:
        print(f"[Lỗi] Không tìm thấy nút 'Tải BCTC' trên {url}.")
    except ElementClickInterceptedException:
        print(f"[Lỗi] Không thể click vào nút trên {url} - Có thể bị che khuất hoặc không tương tác được.")
    except Exception as e:
        print(f"[Lỗi khác] Xảy ra lỗi: {e} trên {url}")
    # Sau khi tương tác, lấy toàn bộ nội dung của trang
    page_source = browser.page_source
    # print(page_source)

    # Tìm thẻ chứa link báo cáo tài chính hợp nhất năm 2024 bằng nội dung hàng
    rows = browser.find_elements(By.CSS_SELECTOR, "table tr")

    text_list = ["báo cáo tài chính hợp nhất năm 2024 (đã kiểm toán)", "báo cáo tài chính năm 2024 (đã kiểm toán)"]
    target_text = (lambda text: text.lower() in text_list)
    found = False
    link_pdf = ""
    for row in rows:
        tds = row.find_elements(By.TAG_NAME, "td")
        for td in tds:
            if target_text(td.text.strip()):
                try:
                    link_td = tds[2]  # Lấy ô thứ 3 trong hàng
                    link_pdf = link_td.find_element(By.TAG_NAME, "a").get_attribute("href")
                    print("Tìm thấy link:", link_pdf)
                    found = True
                    break
                except:
                    print("Không tìm thấy thẻ <a> trong ô thứ 3.")
        if found:
            break

    if not found:
        print("Không tìm thấy dòng chứa nội dung cần tìm.")

    browser.quit()
    return link_pdf

#hàm tải file bctc pdf từ link vừa lấy
def download_pdf(reportCode, link_pdf, pdf_path):
    file_name = f"{reportCode}_HopNhat_2024.pdf"
    file_path = os.path.join(pdf_path, file_name)
    response = requests.get(link_pdf)
    if response.status_code == 200:
        with open(file_path, "wb") as f:
            f.write(response.content)
            print(f"Tải thành công: {file_name}")
    else:
        print(f"Lỗi khi tải file, mã trạng thái: {response.status_code}")

if __name__ == '__main__':
    ReportCode_folder_path = r'D:\CrawlProjects\CrawlFinanceReport\ReportFinance\ReportCode'
    for dirpath, dirname, filenames in os.walk(ReportCode_folder_path):
        for filename in filenames:
            # tạo folder có tên là nhóm cổ phiếu
            csv_path = ""
            name_stock_group = ""
            if filename.lower().endswith(".csv"):  # chỉ lấy file .csv
                csv_path = os.path.join(dirpath, filename)
                name_stock_group = os.path.splitext(filename)[0].strip()  # bỏ .csv và khoảng trắng

            folder_path = r"D:\CrawlProjects\CrawlFinanceReport\ReportFinance"
            pdf_path = os.path.join(folder_path, "ReportFinancePDF")  # tạo folder ReportFinance để
            os.makedirs(pdf_path, exist_ok=True)

            folder_stock_group_path = os.path.join(pdf_path, name_stock_group)
            os.makedirs(folder_stock_group_path, exist_ok=True)

            # lấy link pdf từ browser
            link_pdf = ""
            reportCode = ""
            noReportPDF = []
            df = pd.read_csv(csv_path)
            print(f"Đang thực hiện download BCTC {name_stock_group}")
            for i, row in df.iterrows():
                reportCode = row.iloc[1]
                link_pdf = get_report_pdf_link(reportCode)
                if link_pdf:
                    download_pdf(reportCode, link_pdf, folder_stock_group_path)
                else:
                    print(f"Không tìm thấy link pdf của {reportCode}")
                    noReportPDF.append(reportCode)
                    continue

            noReportPDF_df = pd.DataFrame(noReportPDF, columns=["Mã cổ phiếu"])
            noReportPDF_filename = "Nhóm không có BCTC năm 2024.csv"
            noReportPDF_path = os.path.join(pdf_path, noReportPDF_filename)
            noReportPDF_df.to_csv(noReportPDF_path, index=False, encoding='utf-8-sig')
            print("Lưu thành công file nhóm không có BCTC năm 2024")


