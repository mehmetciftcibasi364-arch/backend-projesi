import sqlite3

DATABASE_NAME = "sensor_data.db"


def create_database():
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT NOT NULL,
            temperature REAL NOT NULL,
            humidity REAL NOT NULL,
            soil_moisture REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


def save_sensor_data(device_id, temperature, humidity, soil_moisture):
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO sensor_data
        (device_id, temperature, humidity, soil_moisture)
        VALUES (?, ?, ?, ?)
    """, (device_id, temperature, humidity, soil_moisture))

    connection.commit()
    connection.close()


def get_sensor_data():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM sensor_data
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    connection.close()

    return [dict(row) for row in rows]