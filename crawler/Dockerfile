FROM python:3.10-slim

# RUN apt-get update && apt-get install -y \
#     chromium chromium-driver \
#     curl unzip gnupg \
#     && apt-get clean



# Cài đặt các gói cần thiết, bao gồm cả wget
RUN apt-get update && apt-get install -y wget curl gnupg unzip

# Cài đặt Google Chrome phiên bản 134.0.6998.117
RUN wget https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_134.0.6998.117-1_amd64.deb \
    && apt-get update \
    && apt install -y ./google-chrome-stable_134.0.6998.117-1_amd64.deb \
    && rm google-chrome-stable_134.0.6998.117-1_amd64.deb \
    && rm -rf /var/lib/apt/lists/*

# Tải và cài đặt ChromeDriver phiên bản 134.0.6998.117
RUN wget -N https://storage.googleapis.com/chrome-for-testing-public/134.0.6998.117/linux64/chromedriver-linux64.zip \
    && unzip chromedriver-linux64.zip \
    && mv chromedriver-linux64/chromedriver /usr/local/bin/ \
    && chmod +x /usr/local/bin/chromedriver \
    && rm -rf chromedriver-linux64*


# # Xác minh cài đặt
# RUN google-chrome --version && chromedriver --version



# ENV CHROME_BIN=/usr/bin/chromium
# ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

WORKDIR /app
COPY . .

RUN pip install --upgrade pip && pip install -r requirements.txt

CMD ["python", "producer.py"]

# CMD ["python", "test_crawl_only.py"]
