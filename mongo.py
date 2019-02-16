#! /usr/bin/env python3

import json
import pymongo
import gridfs
import logging
from pymongo import MongoClient
from gridfs import GridFSBucket
from kafka import KafkaConsumer, KafkaProducer

mongo_client = MongoClient('mongodb://restheart:R3ste4rt!@35.242.180.246:27017')


consumer = KafkaConsumer(
                'mongo-in', 
                bootstrap_servers=['35.246.41.186:9092'],
                value_deserializer=lambda value: json.loads(value))

def get_producer():
    producer = KafkaProducer(
                    bootstrap_servers=['35.246.41.186:9092'])
                    # value_serializer=lambda value: json.dumps(value).encode())
    return producer

for msg in consumer:
    print(msg.value)
    video_title = msg.value
    videos_db = mongo_client.get_database('videos')
    fs        = GridFSBucket(videos_db)
    grid_out  = fs.open_download_stream_by_name(video_title)
    contents  = grid_out.read()
    topic     = 'mongo-out'
    producer  = get_producer()
    print('sending to flask via producer')
    producer.send(topic, value=contents)
    logging.basicConfig(level=logging.INFO)
    print('sent')
    


