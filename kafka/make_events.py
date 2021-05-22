#!/usr/bin/python3
import requests
import json
import threading, logging, time
import multiprocessing
import argparse
#from confluent_kafka import Producer
from kafka import KafkaProducer
import configparser

# from opensky_api import OpenSkyApi

class MyProducer(threading.Thread):
    def __init__(self, topic, delay):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()
        self.topic_name = topic
        self.delay_time = delay

    def stop(self):
        self.stop_event.set()

    def run(self):
        p = KafkaProducer(bootstrap_servers='10.38.10.6:9092')
        while not self.stop_event.is_set():
            messages = call_api()
            print(messages[0])
            for m in messages:
                # print(m)
                future = p.send(self.topic_name, json.dumps(m).encode('utf-8'))
                result = future.get(timeout=60)
            print(f"produced {len(messages)} messages... to {self.topic_name}")
            p.flush()
            # Sleep for x sec between API calls
            print(f"sleeping for {self.delay_time} seconds")
            time.sleep(self.delay_time)


def call_api():
    # Could use new version in the future which binds to API
    # api = OpenSkyApi()
    # s = api.get_states()
    # print(s)

    # Using REST
    print("Starting API call..")
    r = requests.get("https://opensky-network.org/api/states/all",
                     headers={
                         "Accept": "application/json"
                     }
                     )
    if r.status_code != 200:
        print(f"Error. Return code={r.status_code}")
    # Serialize json messages
    messages = []
    data = json.loads(r.text)
    for s in data['states']:
        rec = {
            "icao24": s[0],
            "callsign": s[1].strip(' '),
            "origin_country": s[2],
            "time_position": s[3],
            "last_contact": s[4],
            "lon": s[5],
            "lat": s[6],
            "geo_altitude": s[7],
            "on_ground": s[8],
            "velocity": s[9],
            "heading": s[10]
        }
        if rec['lon'] != None and rec['lat'] != None:
            messages.append(rec)
    return messages


def run_tasks(config):
    tasks = []
    for i in range(0, int(config['DEFAULT']['num_threads'])):
        tasks.append(MyProducer(config['DEFAULT']['topic_name'], int(config['DEFAULT']['delay_time'])))

    for t in tasks:
        t.start()

    # Total Runtime
    time.sleep(int(config['DEFAULT']['runtime'].strip()))
    print("producer shutdown after {runtime} seconds".format(runtime=config['DEFAULT']['runtime']))

    for task in tasks:
        print(f"stopping task {task}")
        task.stop()

    for task in tasks:
        task.join()


def main():
    config = configparser.ConfigParser()
    print(config)
    config.read('kafka.conf')
    #run_tasks(config)
    print(config["DEFAULT"]["topic_name"])

if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s.%(msecs)s:%(name)s:%(thread)d:%(levelname)s:%(process)d:%(message)s',
        level=logging.INFO
    )
    main()
