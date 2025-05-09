import pandas as pd
from time import sleep
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from kafka import KafkaProducer
import json
import os
from kafka.errors import KafkaError
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
    # options.add_argument("--headless=new")  # headless mới ổn định hơn
    options.add_argument("--headless")
    options.add_argument("--incognito")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-crash-reporter")
    options.add_argument("--no-proxy-server")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-web-security")
    options.add_argument("--remote-debugging-port=9222")


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



# Gửi dữ liệu lên Kafka
def send_data_to_kafka(topic):
    url = 'https://investing.com/economic-calendar/cpi-68'
    tableID = '68'
    chrome_driver_path = os.getenv("CHROME_DRIVER_PATH", "/usr/local/bin/chromedriver")

    df = crawlData(url, tableID, chrome_driver_path)

    # Gửi từng dòng dữ liệu lên Kafka
    for _, row in df.iterrows():
        payload = {
            "DateKey": int(row["DateKey"]),
            "CI": float(row["CI"]),
            "CountryID": 1
        }
        print(payload)
        try:
            producer.send(topic, value=payload)
            print(f"Sent to Kafka: {payload}")
        except KafkaError as e:
            print(f"Error sending message to Kafka: {e}")

    print(f"Total records sent: {len(df)}")
    producer.flush()
    producer.close()





# Kiểm tra kết nối Kafka trước khi bắt đầu gửi dữ liệu
def wait_for_kafka(topic):
    while True:
        try:
            metadata = producer.partitions_for(topic)
            if metadata is not None:
                print("Kafka is ready!")
                break
            else:
                print(f"Topic '{topic}' not available yet, retrying...")
        except KafkaError as e:
            print(f"Kafka not ready yet, retrying... {e}")
        time.sleep(5)



# Chạy chương trình
if __name__ == "__main__":
    # Khởi tạo KafkaProducer với serializer
    producer = KafkaProducer(
        bootstrap_servers='kafka:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    topic ="crawldata_Investing"

    # wait_for_kafka()  # Kiểm tra Kafka có sẵn sàng chưa
    send_data_to_kafka(topic)  # Gửi dữ liệu lên Kafka
