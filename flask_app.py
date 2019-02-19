#! /usr/bin/env python3

import json
import pymongo
import gridfs
from pymongo import MongoClient
from gridfs import GridFSBucket
from flask import Flask, render_template, request, url_for, Response, redirect, session
from kafka import KafkaConsumer, KafkaProducer

app            = Flask(__name__)
app.secret_key = b'_5-y4L"F4Q9z\n\x7ec]/'
mongo_client   = MongoClient('mongodb://restheart:R3ste4rt!@35.242.180.246:27017')
mongo_client_2 = MongoClient('mongodb://restheart:R3ste4rt!@35.189.72.90:27017')

def get_postgres_login_consumer():
    postgres_login_consumer = KafkaConsumer(
                'login_response',
                bootstrap_servers=['35.189.65.39:9092'],
                value_deserializer=lambda value: json.loads(value))
    return postgres_login_consumer

def get_postgres_register_consumer():
    postgres_register_consumer = KafkaConsumer(
                'register_response',
                bootstrap_servers=['35.189.65.39:9092'],
                value_deserializer=lambda value: json.loads(value))
    return postgres_register_consumer

def get_postgres_credit_check_consumer():
    postgres_credit_check_consumer = KafkaConsumer(
                'credit-check-response',
                bootstrap_servers=['35.189.65.39:9092'],
                value_deserializer=lambda value: json.loads(value))
    return postgres_credit_check_consumer

def get_postgres_credit_insert_consumer():
    postgres_credit_insert_consumer = KafkaConsumer(
                'credit-insert-response',
                bootstrap_servers=['35.189.65.39:9092'],
                value_deserializer=lambda value: json.loads(value))
    return postgres_credit_insert_consumer

def get_postgres_producer():
    postgres_producer = KafkaProducer(
                bootstrap_servers=['35.189.65.39:9092'],
                value_serializer=lambda value: json.dumps(value).encode())
    return postgres_producer

@app.route('/')
def login() -> 'html':
    session.clear()
    return render_template('super_login.html')

@app.route('/homepage')
def homepage() -> 'html':
    return render_template('image_test.html')

@app.route('/verify_credentials', methods=['POST'])
def verify() -> 'html':
    username = request.form['username']
    session['username'] = username
    password = request.form['password']
    topic    = 'login'
    postgres_producer = get_postgres_producer()
    postgres_producer.send(topic, value=[username, password])
    postgres_login_consumer = get_postgres_login_consumer()
    for msg in postgres_login_consumer:
        response = msg.value
        if response == 0:
            topic = 'credit-check'
            postgres_producer.send(topic, value=username)
            postgres_credit_check_consumer = get_postgres_credit_check_consumer()
            for message in postgres_credit_check_consumer:
                result = message.value 
                if result == 0:
                    return redirect(url_for('homepage'))
                else:
                    return render_template('my_payment.html')
        else:
            return render_template('incorrect_login.html')

@app.route('/register_user', methods = ['POST'])
def register() -> 'html':
    username = request.form['username']
    session['username'] = username
    password = request.form['password']
    topic    = 'register'
    postgres_producer = get_postgres_producer()
    postgres_producer.send(topic, value=[username, password])
    postgres_register_consumer = get_postgres_register_consumer()
    for msg in postgres_register_consumer:
        response = msg.value
        if response == 0:
            return render_template('my_payment.html')
        else:
            return render_template('username_taken.html')

@app.route('/credit_insert', methods=['POST', 'GET'])
def payment_submit() -> 'html':
    username = session['username'] 
    card_name = request.form['card_name']
    card_number = request.form['card_number']
    expiry_month = request.form['expiry_month']
    expiry_year = request.form['expiry_year']
    card_cvv = request.form['card_cvv']
    topic = 'credit-insert'
    postgres_producer = get_postgres_producer()
    postgres_producer.send(topic, value=[username, card_name, card_number, expiry_month, expiry_year, card_cvv])
    postgres_credit_insert_consumer = get_postgres_credit_insert_consumer()
    for msg in postgres_credit_insert_consumer:
        response = msg.value
        if response == 0:
            return redirect(url_for('homepage'))
        else:
            return render_template('credit_insertion_failed.html')

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

@app.route('/showvideo2', methods=['POST', 'GET'])
def show_video_2() -> 'video':
    if request.method == 'POST':
        session['video_title'] = request.form['title']
        videos_db = mongo_client_2.get_database('videos')
        fs        = GridFSBucket(videos_db)
        grid_out  = fs.open_download_stream_by_name(session['video_title'])
        contents  = grid_out.read()
        return Response(contents, mimetype='video/mp4')
    elif request.method == 'GET':
        videos_db = mongo_client_2.get_database('videos')
        fs        = GridFSBucket(videos_db)
        grid_out  = fs.open_download_stream_by_name(session['video_title'])
        contents  = grid_out.read()
        return Response(contents, mimetype='video/mp4')

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

if __name__ == '__main__':
    app.run(debug=True, threaded=True, host='0.0.0.0', port=8080)

# kafka-python documentation reference: https://pypi.org/project/kafka-python/
# PyMongo documentation reference: https://api.mongodb.com/python/current/
# gridfs documentation reference: https://api.mongodb.com/python/current/api/gridfs/index.html
