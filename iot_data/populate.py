import sqlite3
import random
import time
from datetime import datetime, timezone, timedelta

# Define IST manually to avoid needing third-party libraries on Windows
IST = timezone(timedelta(hours=5, minutes=30), 'IST')

def run_simulation():
    devices = ['Sensor_Alpha', 'Sensor_Beta']
    print("Starting continuous IoT data simulation (IST). Press Ctrl+C to stop.")
    
    while True:
        try:
            conn = sqlite3.connect('iot_data.db')
            c = conn.cursor()
            
            # Generate the exact IST string for this batch
            current_ist = datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')
            
            for dev in devices:
                temp = round(random.uniform(20.0, 35.0), 2)
                status = "OK" if temp < 30.0 else "WARNING"
                
                # Insert the explicit IST timestamp into the database
                c.execute(
                    "INSERT INTO telemetry (device_id, temperature, status, timestamp) VALUES (?, ?, ?, ?)", 
                    (dev, temp, status, current_ist)
                )
                print(f"[{current_ist}] Inserted: {dev} | Temp: {temp}°C | Status: {status}")
                
            conn.commit()
            conn.close()
            time.sleep(10)
            
        except KeyboardInterrupt:
            print("\nSimulation stopped.")
            break

if __name__ == '__main__':
    run_simulation()