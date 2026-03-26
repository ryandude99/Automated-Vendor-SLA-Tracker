import requests
from datetime import datetime, timezone
from databaseSetup import insertSlaLog


def getTrain():
    apiKey = "97f2339b5e33444995e1538ba99989a9"
    apiUrl = "https://api-v3.mbta.com/predictions"
    params = {
        "api_key": apiKey,
        "filter[route]": "Red",
    }

    try:
        print("Fetching live data from MBTA...")
        response = requests.get(apiUrl, params=params, timeout=(5,10))
        response.raise_for_status()

        data = response.json()
        return data
    
    except Exception as e:
        print(f"API Error: {e}")
        return None



def slaPayload(trainData):
    if not trainData or "data" not in trainData:
        print("No valid data to process.")
        return
    
    print(f"Successfully pulled {len(trainData['data'])} predictions.\n")
    activeTrains = {}

    for train in trainData["data"]:
        attributes = train.get("attributes", {})
        relationships = train.get("relationships", {})

        arrival_time = attributes.get("arrival_time")
        vehicle = relationships.get("vehicle", {}).get("data")
        stop = relationships.get("stop", {}).get("data")

        if not arrival_time or not vehicle or not stop:        #Handle Missing Data
            continue

        trainID = vehicle.get("id")
        station = stop.get("id")

        try:
            arrivalDT = datetime.fromisoformat(arrival_time.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)

            minutesAway = int((arrivalDT - now).total_seconds() / 60)

            if minutesAway < 0:
                continue
            
            if trainID not in activeTrains or minutesAway < activeTrains[trainID]["minutesAway"]:
                activeTrains[trainID] = {
                    "station": station,
                    "minutesAway": minutesAway
                }
        
        except Exception:
            continue

    
    totalTrains = 0
    totalOnTime = 0
    totalBreaches = 0
    slaThreshold = 5
    
    for trainID, data in activeTrains.items():
        station = data["station"]
        minutesAway = data["minutesAway"]

        if minutesAway > slaThreshold:
            insertSlaLog(trainID, station, minutesAway, True)
            totalBreaches += 1
        else:
            insertSlaLog(trainID, station, minutesAway, False)
            totalOnTime += 1
            
        totalTrains += 1
    
    if totalTrains > 0:
        compliancePercentage = (totalOnTime / totalTrains) * 100
    else:
        compliancePercentage = 0
        
    print(f"Total Trains: {totalTrains}")
    print(f"Total On Time: {totalOnTime}")
    print(f"Total Breaches: {totalBreaches}")
    print(f"SLA Compliance: {compliancePercentage:.1f}%")



if __name__ == "__main__":
    data = getTrain()
    slaPayload(data)
