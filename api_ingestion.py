import requests
from databaseSetup import insertSlaLog


def getTrain():
    apiKey = "03f8a336-4167-4b82-be30-09a3f420257d"
    apiUrl = f"https://developerservices.itsmarta.com:18096/railrealtimearrivals?apiKey={apiKey}"
    
    try:
        print("Fetching live data from MARTA...")
        response = requests.get(apiUrl, timeout=120)
        response.raise_for_status()

        trainData = response.json()
        return trainData
    
    except Exception as e:
        print(f"API Error: Connection failed or Timed Out. Details: {e}")
        return None


def prototypeSlaCheck(trainData):
    if not trainData:
        print("No data received.")
        return

    if isinstance(trainData, dict):
        keys = list(trainData.keys())

        if len(keys) ==1 and isinstance(trainData[keys[0]], list):
            trainData = trainData[keys[0]]  #Unwrap Dictionary
        else:
            print("Marta sent an error:")
            #print(trainData)
            return
    
    print(f"Successfully pulled {len(trainData)} train records.\n")
    print("Testing SLA delays on the first 5 records:")

    for train in trainData[:5]:
        trainID = train.get("TRAIN_ID", "Unknown ID")
        station = train.get("STATION", "Unknown Station")
        waitTime = train.get("WAITING_TIME", "")

        if not waitTime:        #Handle Missing Data
            print (f"Train {trainID} at {station}: Missing Wait Time Data. Flagged")
            continue

        try:
            if waitTime in ["Arriving", "Arrived", "Boarding"]:
                minutesAway = 0
            else:
                minutesAway = int(waitTime.split(" ")[0])
            
            slaThreshold = 15       #15 more than 15 minutes = breach
            if minutesAway > slaThreshold:
                print(f"SLA BREACH: Train {trainID} to {station} is {minutesAway} mins away.")
                insertSlaLog(trainID, station, minutesAway, True)
            else:
                print(f"ON TIME: Train {trainID} to {station} is {minutesAway} mins away.")
                insertSlaLog(trainID, station, minutesAway, False)
            
        
        except ValueError:      #Handles Unexpected Formatting
            print(f"Train {trainID}: Unexpected wait time format. Can not calculate delay.")

if __name__ == "__main__":
    data = getTrain()
    prototypeSlaCheck(data)
