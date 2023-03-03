from flask import Flask, jsonify
from google.transit import gtfs_realtime_pb2
import requests
import datetime
from util import *
from feeds import *

app = Flask(__name__)
bmt_feeds = [gtfs_realtime_pb2.FeedMessage() for i in range(len(BMT_FEEDS))]
irt_feeds = [gtfs_realtime_pb2.FeedMessage() for i in range(len(IRT_FEEDS))]

def getAllTrains(feeds, station_names):
    trains = []
    now = datetime.datetime.now()

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
                            #dt = dt.strftime("%I:%M%p")
                            mins_delta = dt-now
                            mins_left = int(mins_delta.seconds/60)
                            #readable = "%s bound %s train, arriving at %s"%(destination, route_name, dt)
                            if (mins_delta.days==0 and mins_delta.seconds>=0 and mins_delta.microseconds>=0):
                                train_rep = {"route_id": route_name, "destination" : destination, "mins_left" : mins_left}
                                trains.append(train_rep)

    return trains

def getFirstNTrains(n, trains):
    trains.sort(key = lambda t : t["mins_left"])
    n = min(n, len(trains))
    return trains[0:n]


@app.route("/train-schedule/<station_names>")
def train_schedule(station_names):
    #station_names = station_names.split(',')
    mta_api_key = "ZhfhmnhoOd5hnNRtyT2g18qfyMuJp1TA1bSQIvfd"
    responses = []

    bmt_indicators = [ord(station[0])>=65 and ord(station[0])<=90 for station in station_names]
    has_bmt = any(bmt_indicators)
    has_irt = not all(bmt_indicators)
    feeds = []
    feed_urls = []
    if has_bmt:
        feeds = bmt_feeds
        feed_urls = BMT_FEEDS

    if has_irt:
        feeds += irt_feeds
        feed_urls += IRT_FEEDS
        
    for mta_url in feed_urls:
        responses.append(requests.get(mta_url, headers={"x-api-key":mta_api_key}))
    

    for (feed, response) in zip(feeds, responses):
        feed.ParseFromString(response.content)

    # Parse the API response to find the schedule for the F train at the specified station
    trains = getAllTrains(feeds, station_names)
    trains = getFirstNTrains(6, trains)
    
    return trains

if __name__ == "__main__":
    app.run(debug=True)

#train_schedule()

#http://web.mta.info/developers/data/nyct/subway/google_transit.zip

#updateStaticMTAData(STATIC_MTA_DATA_PATH)
#stations = getDictFromCSV(STATION_ID_PATH)
#print(stations[2])
