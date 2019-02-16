#! /usr/bin/env python3

import json
import pymongo
import gridfs
from pymongo import MongoClient
from gridfs import GridFSBucket
from flask import Flask, render_template, request, url_for, Response, redirect, session
from kafka import KafkaConsumer, KafkaProducer

app = Flask(__name__)
app.secret_key = b'_5-y4L"F4Q9z\n\x7ec]/'
mongo_client = MongoClient('mongodb://restheart:R3ste4rt!@35.242.180.246:27017')

# def get_mongo_consumer():
#     mongo_consumer = KafkaConsumer(
#                     'mongo-out', 
#                     bootstrap_servers=['35.246.41.186:9092'])
#                     # value_deserializer=lambda value: json.loads(value))
#     return mongo_consumer

# def get_mongo_producer():
#     mongo_producer = KafkaProducer(
#                     bootstrap_servers=['35.246.41.186:9092'],
#                     value_serializer=lambda value: json.dumps(value).encode())
#     return mongo_producer

def get_postgres_login_consumer():
    postgres_login_consumer = KafkaConsumer(
                'login_response',
                bootstrap_servers=['35.246.41.186:9092'],
                value_deserializer=lambda value: json.loads(value))
    return postgres_login_consumer

def get_postgres_register_consumer():
    postgres_register_consumer = KafkaConsumer(
                'register_response',
                bootstrap_servers=['35.246.41.186:9092'],
                value_deserializer=lambda value: json.loads(value))
    return postgres_register_consumer

def get_postgres_producer():
    postgres_producer = KafkaProducer(
                bootstrap_servers=['35.246.41.186:9092'],
                value_serializer=lambda value: json.dumps(value).encode())
    return postgres_producer



@app.route('/')
def login() -> 'html':
    return render_template('super_login.html')

@app.route('/verify_credentials', methods=['POST'])
def verify() -> 'html':
    username = request.form['username']
    password = request.form['password']
    topic    = 'login'
    postgres_producer = get_postgres_producer()
    postgres_producer.send(topic, value=[username, password])
    postgres_login_consumer = get_postgres_login_consumer()
    for msg in postgres_login_consumer:
        response = msg.value
        if response == 0:
            return render_template('image_test.html')
        else:
            return render_template('incorrect_login.html')

@app.route('/register_user', methods = ['POST'])
def regiser() -> 'html':
    username = request.form['username']
    password = request.form['password']
    topic    = 'register'
    postgres_producer = get_postgres_producer()
    postgres_producer.send(topic, value=[username, password])
    postgres_register_consumer = get_postgres_register_consumer()
    for msg in postgres_register_consumer:
        response = msg.value
        if response == 0:
            return render_template('image_test.html')
        else:
            return render_template('username_taken.html')

@app.route('/showvideo', methods=['POST', 'GET'])
def show_video() -> 'video':
    if request.method == 'POST':
        session['video_title'] = request.form['title']
        videos_db = mongo_client.get_database('videos')
        fs        = GridFSBucket(videos_db)
        grid_out  = fs.open_download_stream_by_name(session['video_title'])
        contents  = grid_out.read()
        return Response(contents, mimetype='video/mp4')
    elif request.method == 'GET':
        videos_db = mongo_client.get_database('videos')
        fs        = GridFSBucket(videos_db)
        grid_out  = fs.open_download_stream_by_name(session['video_title'])
        contents  = grid_out.read()
        return Response(contents, mimetype='video/mp4')


# if request.method == 'POST':
#         video_title = request.form['title']
#         topic = 'mongo-in'
#         mongo_producer = get_mongo_producer()
#         mongo_producer.send(topic, value=video_title)
#         mongo_consumer = get_mongo_consumer()
#         for msg in mongo_consumer:
#             contents = msg.value
#             return Response(contents, mimetype='video/mp4')
#     elif request.method == 'GET':
#         mongo_consumer = get_mongo_consumer()
#         for msg in mongo_consumer:
#             contents = msg.value
#             return Response(contents, mimetype='video/mp4')


if __name__ == '__main__':
    app.run(debug=True, threaded=True, host='0.0.0.0', port=8080)

