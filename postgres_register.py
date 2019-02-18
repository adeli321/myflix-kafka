#! /usr/bin/env python3

import json
import hashlib
import psycopg2
from use_db import UseDatabase
from kafka import KafkaConsumer, KafkaProducer

# conn = psycopg2.connect(host='35.234.143.12',
#                             user='postgres',
#                             password='hellopostgres',
#                             database='postgres')
# cursor = conn.cursor()
# db_config = ("host='35.234.143.12', user='postgres', password='hellopostgres', database='postgres'")

db_config = {'host': '35.234.143.12',
            'user': 'postgres',
            'password': 'hellopostgres',
            'database': 'postgres'}

postgres_register_consumer = KafkaConsumer(
                'register',
                bootstrap_servers=['35.189.65.39:9092'],
                value_deserializer=lambda value: json.loads(value))

def get_postgres_producer():
    postgres_producer = KafkaProducer(
                    bootstrap_servers=['35.189.65.39:9092'],
                    value_serializer=lambda value: json.dumps(value).encode())
    return postgres_producer

def register_user(username, password):
    """ Takes supplied username and password and 
        inserts data into postgres auth table """

    hashed_password = hashlib.sha224(('%s' % password).encode('utf-8')).hexdigest()
    try:
        with UseDatabase(db_config) as cursor:
            cursor.execute('SELECT password FROM authentication WHERE username = %s', (username, ))
            user_exist = cursor.fetchall()
            if user_exist == []:
                cursor.execute('INSERT INTO authentication(username, password) VALUES(%s, %s)', (username, hashed_password))
                return 0
            else:
                return 1
    except ConnectionError as err:
        print('Connection error ', str(err))

for msg in postgres_register_consumer:
    print(msg.value)
    reg   = register_user(*msg.value)
    print(reg)
    topic = 'register_response'
    postgres_producer = get_postgres_producer()
    postgres_producer.send(topic, value=reg)
