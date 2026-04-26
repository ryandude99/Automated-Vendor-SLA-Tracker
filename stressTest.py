import sqlite3
import random
from datetime import datetime, timezone
import time

DB_PATH = 'slaTracker.db'

def overloadTest(records=1000):
    print(f"Starting Overload Test: Inserting {records} records rapidly...")
    startTime = time.time()
    
    try:
        conn = sqlite3.connect(DB_PATH, timeout=2.0)
        cursor = conn.cursor()
        
        for i in range(records):
            trainID = f"TEST-TRAIN-{random.randint(1000, 9999)}"
            station = f"Station-{random.randint(1, 50)}"
            minutesAway = random.randint(6, 45) # Always Trigger Breach
            timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute("""
                INSERT INTO trainSlaLogs (trainID, station, minutesAway, isBreach, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (trainID, station, minutesAway, True, timestamp))
            
        conn.commit()
        conn.close()
        
        endTime = time.time()
        print(f"Overload Test Successful: {records} records in {round(endTime - startTime, 3)} seconds.")
        
    except sqlite3.OperationalError as e:
        print(f"Overload Test FAILED: {e}")

if __name__ == "__main__":
    overloadTest()