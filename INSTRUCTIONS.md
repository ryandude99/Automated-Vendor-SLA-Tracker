# Automated Vendor SLA Tracker
**Group:** 38
**Developer:** Ryan Pham

# Instructions Written By AI

## AI Context & Workflow Guide
**Prompt for LLMs:** You are assisting with the "Automated Vendor SLA Tracker". This project is a Python-based, event-driven Extract, Transform, Load (ETL) pipeline and Alerting Microservice. It utilizes the Boston MBTA public transit API as a proxy to simulate a live data stream of an enterprise vendor's delivery vehicles. Its goal is to continuously ingest nested JSONAPI data, calculate Service Level Agreement (SLA) breaches (delays > 5 minutes), load the metrics into a local SQLite database, and fire throttled real-time alerts to a Slack channel.

When assisting with this repository, prioritize lightweight, self-contained solutions (e.g., SQLite, standard Python libraries, `.env` for secrets) over heavy infrastructure.

---

## 1. System Architecture
This project consists of three core scripts that handle the ETL pipeline and event-driven alerting:

* **`databaseSetup.py` (The "Load" Architecture):**
  * Initializes a local SQLite database named `slaTracker.db`.
  * Creates a relational table named `trainSlaLogs` with schema: `logID` (PK), `trainID` (TEXT), `route` (TEXT), `station` (TEXT), `minutesAway` (INTEGER), `isBreach` (BOOLEAN), and `timestamp` (DATETIME).
  * Uses parameterized queries to securely insert processed SLA metrics.
* **`api_ingestion.py` (The "Extract" and "Transform" Engine):**
  * Connects to the MBTA Predictions API using the `requests` library with exponential backoff for error handling.
  * Parses complex JSONAPI structures (`data`, `attributes`, `relationships`) to extract vehicle, stop, and route IDs.
  * Utilizes timezone-aware datetime math to calculate live ETAs and deduplicates records to track only the immediate next stop.
  * Evaluates the ETA against a 5-minute SLA threshold, logs the data, and calculates an overall "SLA Compliance Percentage."
* **`alertService.py` (The Alerting Microservice):**
  * Operates as a background daemon loop scanning the database for recent SLA breaches.
  * Manages an `alertState` SQLite table to track event state and implement a 15-minute cooldown, preventing alert spam.
  * Formats breach data into a markdown payload and securely posts it to an enterprise Slack channel via Webhook.

---

## 2. Environment Setup
To build and run this project locally, open your terminal and run the following commands to set up your environment:

```powershell
# 1. Initialize a Virtual Environment
python -m venv venv

# 2. Activate the Environment (Windows PowerShell)
.\venv\Scripts\activate

# 3. Install Dependencies
pip install requests python-dotenv
```

**Security & API Setup:**
You must create a local `.env` file in the root directory to store your secrets. This file is ignored by Git. 
1. Create a file named `.env`.
2. Add your Slack Webhook URL to the file:
   `SLACK_WEBHOOK_URL="your_slack_webhook_url_here"`
3. Ensure you have an active MBTA Developer API Key assigned to the `apiKey` variable in `api_ingestion.py`.

---

## 3. Execution Instructions
The architecture relies on running the data ingestion pipeline and the alerting microservice simultaneously in two separate terminal windows.

**Terminal 1: The ETL Pipeline**
```powershell
# Step 1: Initialize the Database (Creates slaTracker.db and tables)
python databaseSetup.py

# Step 2: Run the ETL Pipeline (Pulls live MBTA data, checks SLAs, and saves to DB)
python api_ingestion.py
```

**Terminal 2: The Alerting Microservice**
```powershell
# Step 3: Start the Daemon (Scans the DB and fires Slack alerts)
python alertService.py
```

---

## 4. Testing and Validation
* **Database Load Validation:** Install an SQLite viewer extension (e.g., "SQLite Viewer" for VS Code). Open `slaTracker.db` and click the refresh icon to verify that parsed records (including the new `route` column) are inserting correctly.
* **Microservice Validation:** When `api_ingestion.py` logs a breach (>5 mins), verify that `alertService.py` detects it within 60 seconds and pushes a formatted Markdown alert to your designated Slack workspace. Verify that subsequent runs within 15 minutes do not trigger duplicate Slack messages for the same train.