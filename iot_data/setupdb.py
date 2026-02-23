import sqlite3

def create_db():
    conn = sqlite3.connect('iot_data.db')
    c = conn.cursor()
    
    # We drop the old table if it exists to ensure a clean slate for the new timestamps
    c.execute('DROP TABLE IF EXISTS telemetry')
    
    # Notice: 'timestamp' is now just a standard DATETIME column, no default
    c.execute('''
        CREATE TABLE telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT,
            temperature REAL,
            status TEXT,
            timestamp DATETIME
        )
    ''')
    conn.commit()
    conn.close()
    print("Database recreated. Ready for explicit IST timestamps.")

if __name__ == '__main__':
    create_db()