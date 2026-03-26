import sqlite3
import requests
import time
import os
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()
WEBHOOKURL = os.getenv("SLACK_WEBHOOK_URL")

COOLDOWN = 15   # Minutes



def setupAlertState():
    conn = sqlite3.connect("slaTracker.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alertState (
            trainID TEXT PRIMARY KEY,
            lastAlertTime DATETIME
        )
    """)
    conn.commit()
    conn.close()



def sendSlackAlert(trainID, station, minutesAway):
    message = {
        "text": f"SLA BREACH DETECTED!\nTrain ID: {trainID}\nNext Stop: {station}\nDelay Severity: {minutesAway} minutes away"
    }

    try:
        response = requests.post(WEBHOOKURL, json=message)
        response.raise_for_status()
        print(f"Alert successfully fired to Slack for Train {trainID}")
    except Exception as e:
        print(f"Failed to send Slack alert: {e}")


def checkAndAlert():
    conn = sqlite3.connect("slaTracker.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT trainID, station, minutesAway
        FROM trainSlaLogs
        WHERE isBreach = 1
        AND timestamp >= datetime("now", "-10 minutes")
    """)
    recentBreaches = cursor.fetchall()

    for breach in recentBreaches:
        trainID, station, minutesAway = breach

        cursor.execute("""
            SELECT lastAlertTime
            FROM alertState
            WHERE trainID = ?
        """, (trainID,)
        )
        result = cursor.fetchone()

        shouldAlert = False
        now = datetime.now(timezone.utc)

        if result is None:
            shouldAlert = True
        else:
            lastAlertTime = datetime.fromisoformat(result[0])
            minsSinceLastAlert = (now - lastAlertTime).total_seconds() / 60

            if minsSinceLastAlert >= COOLDOWN:
                shouldAlert = True
        
        if shouldAlert:
            sendSlackAlert(trainID, station, minutesAway)

            cursor.execute("""
                INSERT INTO alertState (trainID, lastAlertTime)
                VALUES (?, ?)
                ON CONFLICT(trainID) DO UPDATE SET lastAlertTime = ?
            """, (trainID, now.isoformat(), now.isoformat())
            )
            conn.commit()
    conn.close()


if __name__ == "__main__":
    print("Starting Slack SLA Alerting Microservice...")
    setupAlertState()

    while True:
        currTime = datetime.now().strftime("%H:%M:%S")
        print(f"({currTime}): Scanning database for new SLA breaches...")

        checkAndAlert()
        time.sleep(60)