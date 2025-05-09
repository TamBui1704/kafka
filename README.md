# Kafka Macro Market ETL Project

Dự án nhỏ giúp bạn thực hành Kafka bằng cách:
- Thu thập dữ liệu vĩ mô từ một API công khai
- Gửi dữ liệu đó vào Kafka (Producer)
- Đọc dữ liệu từ Kafka và lưu vào PostgreSQL (Consumer)

## Công nghệ sử dụng
- Apache Kafka & Zookeeper
- PostgreSQL
- Python (`kafka-python`, `requests`, `psycopg2-binary`)
- Docker & Docker Compose

## Cài đặt

1. **Clone project và khởi tạo Docker**:
```bash
docker-compose up -d
```

2. **Tạo môi trường Python và cài thư viện**:
```bash
python -m venv venv
source venv/bin/activate  # hoặc .\venv\Scripts\activate trên Windows
pip install -r requirements.txt
```

3. **Chạy Producer (gửi dữ liệu)**:
```bash
python producer.py
```

4. **Chạy Consumer (đọc và ghi dữ liệu)**:
```bash
python consumer.py
```

## Kết quả mong đợi
- Kafka sẽ chứa các message JSON dạng `{"time": ..., "count": ...}`
- PostgreSQL sẽ lưu thông tin trong bảng `macro_stats`

## Ghi chú
- Có thể dùng DBeaver hoặc psql để kiểm tra dữ liệu trong DB PostgreSQL.
- Kafka topic tên là `macro_topic`.

## Mở rộng
- Có thể chuyển sang stream dữ liệu thời tiết, tỷ giá, chứng khoán…
- Áp dụng thêm công cụ như Airflow để lên lịch hoặc Grafana để hiển thị.