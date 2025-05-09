import pandas as pd
from time import sleep
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time

# Chuyển đổi tháng tiếng Anh thành số
def convert_month(month):
    month_dict = {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
    }
    return month_dict.get(month, 0)

# Khởi tạo trình duyệt
def declare_browser(chrome_driver_path):
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--headless")
    options.add_argument("--incognito")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-crash-reporter")
    options.add_argument("--no-proxy-server")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-web-security")
    options.add_argument("--remote-debugging-port=9222")

    # # # # Dành cho WSL nếu bạn dùng chromium
    # options.binary_location = "/snap/bin/chromium"  # Kiểm tra lại đường dẫn thực tế của bạn


    service = Service(chrome_driver_path)
    browser = webdriver.Chrome(service=service, options=options)
    return browser

# Crawl dữ liệu từ Investing
def crawlData(url, TableID, chrome_driver_path):
    browser = declare_browser(chrome_driver_path)
    browser.get(url)
    sleep(2)

    try:
        cookie = {'name': 'r_p_s_n', 'value': '1'}
        browser.add_cookie(cookie)
        browser.refresh()
        sleep(1)
    except Exception as e:
        print("Cookie setup error:", e)

    df = pd.DataFrame(columns=['DateKey', 'CI'])
    try:
        table = browser.find_element(By.ID, 'eventHistoryTable' + TableID)
        i = -1
        for row in table.find_elements(By.TAG_NAME, 'tr'):
            data = row.find_elements(By.TAG_NAME, 'td')
            if data:
                datetext = data[0].text.strip()[:-1]
                monthEN = datetext[-3:]
                month = convert_month(monthEN)
                if datetext[13:14] == '(':
                    if month == 12 and convert_month(datetext[:3]) == 1:
                        Datekey = (int(datetext[8:12]) - 1) * 10000 + month * 100 + 1
                    else:
                        Datekey = int(datetext[8:12]) * 10000 + month * 100 + 1
                    CI_text = data[2].text.strip()
                    CI = CI_text[:-1]
                    if CI != '':
                        i += 1
                        df.loc[i] = [Datekey, CI]
    except Exception as e:
        print("Error during data extraction:", e)
    finally:
        browser.quit()

    return df

# Test crawl
if __name__ == "__main__":
    start = time.time()
    url = 'https://investing.com/economic-calendar/cpi-68'
    tableID = '68'
    chrome_driver_path = '/usr/local/bin/chromedriver'
    # chrome_driver_path = '/usr/bin/chromedriver'

    df = crawlData(url, tableID, chrome_driver_path)
    print(df)
    print("Load page:", time.time() - start)
