#! /usr/bin/env python3

import json
import hashlib
import psycopg2
from use_db import UseDatabase
from kafka import KafkaConsumer, KafkaProducer

db_config = {'host': '35.234.143.12',
            'user': 'postgres',
            'password': 'hellopostgres',
            'database': 'postgres'}

postgres_login_consumer = KafkaConsumer(
                'login',
                bootstrap_servers=['35.189.65.39:9092'],
                value_deserializer=lambda value: json.loads(value))

def get_postgres_producer():
    postgres_producer = KafkaProducer(
                    bootstrap_servers=['35.189.65.39:9092'],
                    value_serializer=lambda value: json.dumps(value).encode())
    return postgres_producer

def test_auth(username, password):
    """ Queries Postgres instance to check if username/password combination 
    is correct & exists """

    hashed_input_password = hashlib.sha224(('%s' % password).encode('utf-8')).hexdigest()
    try: 
        with UseDatabase(db_config) as cursor:
            cursor.execute('SELECT password FROM authentication WHERE username = %s', (username, ))
            password = cursor.fetchone()
            if password != None:
                password = ''.join(password)
                if password == hashed_input_password:
                    return 0
                else:
                    return 1
            else:
                return 1
    except ConnectionError as err:
        print('Is your db switched on? Error ', str(err))

for msg in postgres_login_consumer:
    print(msg.value)
    auth  = test_auth(*msg.value)
    print(auth)
    topic = 'login_response'
    postgres_producer = get_postgres_producer()
    postgres_producer.send(topic, value=auth)
