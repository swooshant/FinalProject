#!/usr/bin/python3

import json
import pymongo
import pika
import socket
import sys
import threading

# RabbitMQ Global data
username = "team16"
password = "ece4564"
address = "MUST_BE_FILLED_IN"
port = 5672
queue_name = "brogrammers"

# Bluetooth Global data
hostMAC = "MUST_BE_FILLED_IN"
port = 25
backlog = 10
size = 4096


class GPSClient(object):

    def __init__(self, address, port, queue_name, username, password):
        self.queue_name = queue_name
        self.credentials = pika.PlainCredentials(username, password)
        self.params = pika.ConnectionParameters(address,
                                                port,
                                                '/',
                                                self.credentials)
        self.connection = pika.BlockingConnection(self.params)

        self.channel = self.connection.channel()
        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self.callback_queue)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self):
        self.body = "get"
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.props = pika.BasicProperties(
            reply_to=self.callback_queue,
            correlation_id=self.corr_id)
        self.channel.basic_publish(exchange='',
                                   routing_key=self.queue_name,
                                   properties=self.props,
                                   body=self.body)
        # break when all the messages are read for pull
        while self.response is None:
            self.connection.process_data_events()
        return self.response


class Worker(threading.Thread):

    def __init__(self, sock, address):
        threading.Thread.__init__(self)
        self.sock = sock
        self.address = address
        print("Init MongoDB")
        client = pymongo.MongoClient('mongodb://localhost:27017/')
        db = client.repository
        self.collection = db.wifi

    def run(self):
        # Init an RPC Client to talk to GPS module
        print("Create GPS RPC Client object")
        myGPSClient = GPSClient(address, port, queue_name, username, password)

        # Recieve the wifi payload data
        print("Recieve a wifi data payload")
        wifi_payload = self.sock.recv(size)
        self.sock.close()
        print("Recieved bluetooth data: %s", wifi_payload)

        # Get the current location from the GPS module
        print("Make RPC call to GPS module")
        gps_payload = myGPSClient.call()
        print("Recieved location data: %s", gps_payload)

        # Add the GPS data to the Wifi data
        final_payload = []
        print("Create final payload")
        for wifi_item in wifi_payload:
            temp_item = {}
            temp_item["name"] = wifi_item["name"]
            temp_item["data"] = {**item["data"], **gps_payload}
            print("Add new combined item to final payload")
            final_payload.append(newEntry)
            print("Inserted following new item into final payload: %s" % temp_item)

        # Insert the combined data into MongoDB
        print("Insert final data into MongoDB")
        result = self.collection.insert_many(final_payload)


if __name__ == '__main__':
    print("Setting up bluetooth socket")
    s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM,
                      socket.BTPROTO_RFCOMM)
    s.bind((hostMAC, port))
    s.listen(backlog)
    print("Now listening for bluetooth connections")

    while True:
        print("Waiting for client to connect")
        client, address = s.accept()
        print("Create and spawn worker bluetooth thread")
        myWorker = (client, address)
        myWorker.start()
        print("Spawned worker thread")

    s.close()
