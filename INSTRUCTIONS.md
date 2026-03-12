# Automated Vendor SLA Tracker
**Group:** 38
**Developer:** Ryan Pham

# Instructions Written By AI

## AI Context & Workflow Guide
**Prompt for LLMs:** You are assisting with the "Automated Vendor SLA Tracker". This project is a Python-based, event-driven Extract, Transform, Load (ETL) pipeline. It utilizes the MARTA public transit API as a proxy to simulate a live data stream of an enterprise vendor's delivery vehicles. Its goal is to continuously ingest unstructured JSON data, calculate Service Level Agreement (SLA) breaches (delays > 15 minutes), and load the metrics into a local relational database. 

When assisting with this repository, prioritize lightweight, self-contained solutions (e.g., SQLite, standard Python libraries) over heavy infrastructure.

---

## 1. System Architecture
This project currently consists of two core scripts that handle the ETL pipeline:

* **`databaseSetup.py` (The "Load" Architecture):**
  * Initializes a local SQLite database named `slaTracker.db`.
  * Creates a relational table named `trainSlaLogs` with schema: `logID` (PK), `trainID` (TEXT), `station` (TEXT), `minutesAway` (INTEGER), `isBreach` (BOOLEAN), and `timestamp` (DATETIME).
  * Contains the `insertSlaLog()` function, which uses parameterized queries to insert processed SLA metrics into the database securely.
* **`api_ingestion.py` (The "Extract" and "Transform" Engine):**
  * Connects to the MARTA Real-Time Rail API using the `requests` library.
  * Employs a `User-Agent` header disguise and a 120-second timeout to bypass firewall blocks and handle server instability.
  * Contains logic to unwrap nested JSON dictionaries to extract the core vehicle data list.
  * Evaluates the `WAITING_TIME` of each train against a 15-minute SLA threshold.
  * Calls `insertSlaLog()` from the database script to persistently store the evaluated records.

---

## 2. Environment Setup
To build and run this project locally, open your terminal and run the following commands to set up your environment:

```powershell
# 1. Initialize a Virtual Environment
python -m venv venv

# 2. Activate the Environment (Windows PowerShell)
.\venv\Scripts\activate

# 3. Install Dependencies
pip install requests
```

**API Key Setup:**
Ensure you have a valid MARTA Developer API key. Open `api_ingestion.py` and replace the `apiKey` variable string with your active key before running the scripts.

---

## 3. Execution Instructions
The pipeline must be executed in the following order to ensure the storage architecture exists before data is ingested. Run these commands in your terminal:

```powershell
# Step 1: Initialize the Database (Creates slaTracker.db and tables)
python databaseSetup.py

# Step 2: Run the ETL Pipeline (Pulls live data, checks SLAs, and saves to DB)
python api_ingestion.py
```

*Expected Output:* The terminal will display the live extraction status and print a prototype slice (5 records) detailing whether each train is `ON TIME` or an `SLA BREACH`.

---

## 4. Testing and Validation
To verify that the database load logic is functioning correctly:
1. Install an SQLite viewer extension (e.g., "SQLite Viewer" for VS Code).
2. Open the `slaTracker.db` file in your workspace.
3. If records do not appear immediately after running the ingestion script, click the **Refresh** icon in the viewer to clear the cache and load the latest binary data.