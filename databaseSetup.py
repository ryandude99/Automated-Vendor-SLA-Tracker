import sqlite3

def connectDatabase():
    conn = sqlite3.connect("slaTracker.db")
    cursor = conn.cursor()
    print("Connecting to SQLite")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trainSlaLogs (
            logID INTEGER PRIMARY KEY AUTOINCREMENT,
            trainID TEXT,
            station TEXT,
            minutesAway INTEGER,
            isBreach BOOLEAN,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print("Database 'slaTracker.db' and 'trainSlaLogs' table successfully connected!")

def insertSlaLog(trainID, station, minutesAway, isBreach):
    conn = sqlite3.connect("slaTracker.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO trainSlaLogs (trainID, station, minutesAway, isBreach) 
        VALUES (?, ?, ?, ?)
    """, (trainID, station, minutesAway, isBreach))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    connectDatabase()