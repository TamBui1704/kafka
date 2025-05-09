from kafka import KafkaConsumer
import json
import psycopg2
import os

# Kết nối PostgreSQL
conn = psycopg2.connect(
    dbname="DWH_Economy",
    user="user",
    password="password",
    host="postgres",
    port="5432"
)
cursor = conn.cursor()

# Kafka consumer
consumer = KafkaConsumer(
    'crawldata_Investing',
    bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
    group_id='investing-group',
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

print("Consumer is listening to topic 'crawldata_Investing'...")

# Đảm bảo table đã tồn tại (tùy bạn tạo riêng hoặc để consumer tạo)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS crawldata (
        date_key INTEGER,
        ci REAL,
        country_id INTEGER
    );
""")
conn.commit()

# Ghi từng record vào PostgreSQL
for message in consumer:
    data = message.value
    print(f"Received message: {data}")
    cursor.execute(
        "INSERT INTO crawldata (date_key, ci, country_id) VALUES (%s, %s, %s);",
        (data['DateKey'], data['CI'], data['CountryID'])
    )
    conn.commit()
