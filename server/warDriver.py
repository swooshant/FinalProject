#!/usr/bin/python3

import json
import pymongo
import pika
import socket
import sys
import threading
import uuid

# RabbitMQ Global data
username = 'team16'
password = 'ece4564'
host = '172.30.124.234'
port = 5672
queue_name = 'brogrammers'

# Bluetooth Global data
hostMAC = '10:02:B5:3B:D4:C6'
port = 25
backlog = 5


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

    def __init__(self, sock, address, threadNum):
        threading.Thread.__init__(self)
        self.sock = sock
        self.address = address
        self.threadNum = threadNum

        # Configure mongodb
        print("Thread #%d: Init MongoDB" % threadNum)
        client = pymongo.MongoClient('mongodb://localhost:27017/')
        db = client.wifidata
        self.collection = db.accesspoints
        self.collection.create_index([("quality", pymongo.ASCENDING),
                                      ("frequency", pymongo.ASCENDING),
                                      ("encryption", pymongo.ASCENDING),
                                      ("address", pymongo.TEXT),
                                      ("signal", pymongo.ASCENDING),
                                      ("name", pymongo.ASCENDING),
                                      ("channel", pymongo.ASCENDING),
                                      ("lat", pymongo.ASCENDING),
                                      ("lon", pymongo.ASCENDING),
                                      ("time", pymongo.ASCENDING)],
                                     unique=True)

        # Socket timeout change
        # self.sock.setblocking(True)

    def run(self):
        # Init an RPC Client to talk to GPS module
        print("Thread #%d: Create GPS RPC Client object" % self.threadNum)
        myGPSClient = GPSClient('172.30.124.234', 5672,
                                'brogrammers', 'team16', 'ece4564')

        # Recieve the wifi payload data
        print("Thread #%d: Recieve a wifi data payload" % self.threadNum)
        wifi_payload = self.recvall()
        wifi_payload = wifi_payload.decode('utf-8')
        wifi_payload = json.loads(wifi_payload)
        self.sock.close()
        print("Thread #%d: Recieved bluetooth data" % self.threadNum)

        # Get the current location from the GPS module
        print("Thread #%d: Make RPC call to GPS module" % self.threadNum)
        gps_payload = myGPSClient.call()
        print(gps_payload)
        if gps_payload == b'error':
            print(
                "Thread #%d: GPS unable to make location lock, discarding data" % self.threadNum)
            sys.exit()
        gps_payload = gps_payload.decode('utf-8')
        gps_payload = json.loads(gps_payload)
        print("Thread #%d: Recieved location data" % self.threadNum)

        # Add the GPS data to the Wifi data
        final_payload = []
        print("Thread #%d: Create final payload" % self.threadNum)
        for wifi_item in wifi_payload:
            newEntry = {**wifi_item, **gps_payload}
            final_payload.append(newEntry)

        # Insert the combined data into MongoDB
        print("Thread #%d: Insert final data into MongoDB" % self.threadNum)
        try:
            print("Number of entries being added to DB: %d" %
                  len(final_payload))
            result = self.collection.insert_many(final_payload)
        except pymongo.errors.BulkWriteError as bwe:
            print("Discarding duplicate entries")
        return 0

    # Function which wraps the recv call to make sure we get the whole payload
    def recvall(self):
        BUFF_SIZE = 1024  # 1 KiB
        data = b''
        while data[-1:] != b']':
            part = self.sock.recv(BUFF_SIZE)
            data += part
        return data


if __name__ == '__main__':
    print("Master Thread: Setting up bluetooth socket")
    s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM,
                      socket.BTPROTO_RFCOMM)
    s.bind((hostMAC, port))
    s.listen(backlog)
    print("Master Thread: Now listening for bluetooth connections")
    btConnectionCnt = 1

    try:
        while True:
            print("Master Thread: Waiting for client to connect")
            client, address = s.accept()
            print("Master Thread: Create and spawn worker bluetooth thread")
            myWorker = Worker(client, address, btConnectionCnt)
            myWorker.start()
            print("Master Thread: Spawned worker thread number %d" %
                  btConnectionCnt)
            btConnectionCnt += 1
    except KeyboardInterrupt:
        print("Closing socket and channel")
        s.close()
