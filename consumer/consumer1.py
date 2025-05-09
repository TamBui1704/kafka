from kafka import KafkaConsumer
import json
import psycopg2
import time
import os

# Thử kết nối Kafka với backoff
def connect_kafka(topic):
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers='kafka:9092',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest',  # đọc từ đầu
        enable_auto_commit=False       # không commit offset
    )
    return consumer

# Kết nối tới PostgreSQL
def connect_postgres():
    conn = psycopg2.connect(
                                dbname=os.getenv("POSTGRES_DB", "datawarehouse"),
                                user=os.getenv("POSTGRES_USER", "postgres"),
                                password=os.getenv("POSTGRES_PASSWORD", "password"),
                                host=os.getenv("POSTGRES_HOST", "postgres"),
                                port=os.getenv("POSTGRES_PORT", "5432")
                            )
    return conn
       

# Tạo bảng nếu chưa tồn tại
def create_table(cursor, conn, table):
    cursor.execute(f"""
        CREATE SCHEMA IF NOT EXISTS fact;
    """)
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table} (
            yoy_ci_percent DECIMAL(18, 2),
            mom_cpi_percent DECIMAL(18, 2),
            lai_suat_hien_hanh DECIMAL(18, 2),
            pmi_phi_san_xuat DECIMAL(18, 2),
            pmi_san_xuat DECIMAL(18, 2),
            ty_le_that_nghiep DECIMAL(18, 2),
            gia_tri_xuat_khau DECIMAL(18, 2),
            yoy_cpi_percent DECIMAL(18, 2),
            gia_tri_nhap_khau DECIMAL(18, 2),
            quoc_gia_id INT,
            nganh_id INT,
            date_key INT
        );
    """)
    conn.commit()

def main():

    topic ="crawldata_Investing"
    try:
        # Kết nối Kafka
        consumer = connect_kafka(topic)
        
        # Kết nối PostgreSQL
        conn = connect_postgres()
        cursor = conn.cursor()
        
        # Tạo bảng
        create_table(cursor, conn)
        
        print("Đã kết nối tới Kafka và PostgreSQL, đang đợi tin nhắn...")
        
        table ="fact.economic_index"
        # Xử lý tin nhắn
        for msg in consumer:
            data = msg.value
            print(f"Nhận: {data}")
            cursor.execute(
                f"INSERT INTO {table} (date_key, yoy_ci_percent, quoc_gia_id) VALUES (%s, %s, %s)",
                (data['DateKey'], data['CI'], data['CountryID'])
            )
            conn.commit()
    
    except KeyboardInterrupt:
        print("Đang dừng consumer...")
    except Exception as e:
        print(f"Lỗi không xác định: {e}")
    finally:
        # Đóng kết nối khi kết thúc
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        if 'consumer' in locals():
            consumer.close()
        print("Đã đóng tất cả các kết nối")


if __name__ == "__main__":
    main()