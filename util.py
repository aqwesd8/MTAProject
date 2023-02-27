import urllib.request
import zipfile
import io
import csv
from collections import defaultdict

STATIC_MTA_DATA_PATH = "static_mta_data"
STATION_ID_PATH = STATIC_MTA_DATA_PATH+"/stops.txt"

station_id_to_name = defaultdict(lambda: None)

### SUBWAY HELPER FUNCTIONS ###

def updateStaticMTAData(static_mta_path):
    # Set the URL of the zip file to download
    url = "http://web.mta.info/developers/data/nyct/subway/google_transit.zip"
    # Download the zip file
    with urllib.request.urlopen(url) as response:
        data = response.read()

    # Unzip the file
    with zipfile.ZipFile(io.BytesIO(data)) as zip_ref:
        zip_ref.extractall(static_mta_path)

def getDictFromCSV(csv_file_path):
    data = []

    with open(csv_file_path, "r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            data.append(row)

    return data

#updateStaticMTAData(STATIC_MTA_DATA_PATH)
STATIONS = getDictFromCSV(STATION_ID_PATH)

def getStationNameFromID(station_id):
    station_name = station_id_to_name[station_id]
    if station_name:
        return station_name
    for station in STATIONS:
        if station["stop_id"] == station_id:
            station_name = station["stop_name"]
            station_id_to_name[station_id] = station_name
            return station_name
