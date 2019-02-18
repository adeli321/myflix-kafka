#! /usr/bin/env python3

import json
import psycopg2
from use_db import UseDatabase
from kafka import KafkaConsumer, KafkaProducer

db_config = {'host': '35.234.143.12',
            'user': 'postgres',
            'password': 'hellopostgres',
            'database': 'postgres'}

postgres_credit_check_consumer = KafkaConsumer(
                'credit-insert',
                bootstrap_servers=['35.189.65.39:9092'],
                value_deserializer=lambda value: json.loads(value))

def get_postgres_credit_check_producer():
    postgres_credit_check_producer = KafkaProducer(
                    bootstrap_servers=['35.189.65.39:9092'],
                    value_serializer=lambda value: json.dumps(value).encode())
    return postgres_credit_check_producer

def test_auth(username, card_name, card_number, expiry_month, expiry_year, card_cvv):
    """ Queries Postgres instance to check if username/password combination 
    is correct & exists """

    try: 
        with UseDatabase(db_config) as cursor:
            cursor.execute('INSERT INTO credit(username, card_name, card_number, expiry_month, expiry_year, card_cvv) VALUES(%s, %s, %s, %s, %s, %s)', 
                            (username, card_name, card_number, expiry_month, expiry_year, card_cvv))
            return 0
    except ConnectionError as err:
        print('Is your db switched on? Error ', str(err))

for msg in postgres_credit_check_consumer:
    print(*msg.value)
    auth  = test_auth(*msg.value)
    print(auth)
    topic = 'credit-insert-response'
    postgres_credit_check_consumer = get_postgres_credit_check_producer()
    postgres_credit_check_consumer.send(topic, value=auth)
