import sqlite3
import random
import time
from datetime import datetime

def continuous_populate():
    conn = sqlite3.connect('iot_data.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS device_telemetry 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      device_id TEXT, 
                      reading REAL, 
                      status TEXT, 
                      timestamp DATETIME)''')
    conn.commit()

    devices = ['Sensor_Alpha', 'Sensor_Beta']
    print(f"[*] Starting continuous simulation. Press Ctrl+C to stop.")

    try:
        while True:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for dev in devices:
                # Simulate a random walk for temperature
                val = round(random.uniform(20.0, 30.0), 2)
                status = "OK" if val < 28.5 else "CRITICAL"
                
                cursor.execute("INSERT INTO device_telemetry (device_id, reading, status, timestamp) VALUES (?,?,?,?)",
                               (dev, val, status, timestamp))
                print(f"[{timestamp}] Inserted: {dev} | Value: {val} | Status: {status}")
            
            conn.commit()
            time.sleep(10) # Updates every 10 seconds
    except KeyboardInterrupt:
        print("\n[!] Simulation stopped.")
    finally:
        conn.close()

if __name__ == "__main__":
    continuous_populate()