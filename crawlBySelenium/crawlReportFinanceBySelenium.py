from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from CrawlFinanceReport.ReportFinance.crawlFinanceReport import link_pdf

chrome_options = Options()
# chrome_options.add_argument("--headless")

#1. Tạo service object, trỏ đến đường dẫn chromedriver
driver_path = ChromeDriverManager().install()
service = Service(driver_path)

#2. Khởi tạo trình duyệt
browser = webdriver.Chrome(service=service, options=chrome_options)

#3. Mở trang web
url = f"https://cafef.vn/du-lieu/hose/ACB.chn"
browser.get(url)

# Kiểm tra xem có nút "Tải BCTC" hay không và nhấn vào
try:
    tab = WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.XPATH, "/html/body/form/div[3]/div[2]/div[1]/div[5]/div[1]/div[11]/div[2]/div[1]/ul/li[4]/a"))
    )
    sleep(5)
    tab.click()
    print("Đã click vào nút Tải BCTC.")
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

# #tìm thẻ chứa link bctc hợp nhất năm 2024 (đã kiểm toán) bằng XPATH cụ thể
# # => không nên dùng vì thứ tự thẻ sẽ thay đổi theo năm, không thể lấy chính xác bctc hợp nhất năm 2024
# bctc_element = browser.find_element(By.CSS_SELECTOR, "#divDocument > div > table > tbody > tr:nth-child(3) > td:nth-child(3) > a")
#
# #lấy href bctc hợp nhất 2024 (đã kiểm toán) từ thẻ vừa tìm
# href_bctc = bctc_element.get_attribute("href")
# # print(href_bctc)

# Tìm thẻ chứa link báo cáo tài chính hợp nhất năm 2024 bằng nội dung hàng
rows = browser.find_elements(By.CSS_SELECTOR, "table tr")

target_text = "báo cáo tài chính hợp nhất năm 2024 (đã kiểm toán)".lower()
found = False
link_pdf = ""
for row in rows:
    tds = row.find_elements(By.TAG_NAME, "td")
    for td in tds:
        if target_text in td.text.strip().lower():
            try:
                link_td = tds[2]  # Lấy ô thứ 3 trong hàng
                link_pdf = link_td.find_element(By.TAG_NAME, "a").get_attribute("href")
                # print("Tìm thấy link:", link_pdf)
                found = True
                break
            except:
                print("Không tìm thấy thẻ <a> trong ô thứ 3.")
    if found:
        break

if not found:
    print("Không tìm thấy dòng chứa nội dung cần tìm.")

browser.quit()

