from flask import Flask, jsonify
from google.transit import gtfs_realtime_pb2
import requests
import datetime
from util import *
from feeds import *

app = Flask(__name__)

@app.route("/train-schedule/<station_names>")
def train_schedule(station_names):
    station_names = station_names.split(',')
    mta_api_key = "ZhfhmnhoOd5hnNRtyT2g18qfyMuJp1TA1bSQIvfd"

    feeds = [gtfs_realtime_pb2.FeedMessage() for i in range(len(ALL_FEEDS))]
    responses = []
    for mta_url in ALL_FEEDS:
        responses.append(requests.get(mta_url, headers={"x-api-key":mta_api_key}))
    

    for (feed, response) in zip(feeds, responses):
        feed.ParseFromString(response.content)

    # Parse the API response to find the schedule for the F train at the specified station
    out = []
    for feed in feeds:
        for train in feed.entity:
            if train.HasField('trip_update'):
                for stop_time in train.trip_update.stop_time_update:
                    for station_name in station_names:
                        if station_name in stop_time.stop_id:
                            route_name = train.trip_update.trip.route_id
                            destination_id = train.trip_update.stop_time_update[-1].stop_id
                            destination = getStationNameFromID(destination_id)
                            dt = datetime.datetime.fromtimestamp(stop_time.arrival.time)
                            dt = dt.strftime("%I:%M%p")
                            readable = "%s bound %s train, arriving at %s"%(destination, route_name, dt)
                            out.append(readable)
    
    return out

if __name__ == "__main__":
    app.run(debug=True)

#train_schedule()

#http://web.mta.info/developers/data/nyct/subway/google_transit.zip

#updateStaticMTAData(STATIC_MTA_DATA_PATH)
#stations = getDictFromCSV(STATION_ID_PATH)
#print(stations[2])