# -- Gps Pi code #
import gpsd
import json
import pika
import socket
import sys
import uuid
import time
from datetime import datetime

username = 'team16'
password = 'ece4564'
address = '127.0.0.1'
port = 5672
queue_name = 'brogrammers'

latitude = 37.232944
longitude = -80.422957

def on_request(ch, method, props, body):
		global latitude
		global longitude
		jsonReply = {}
		try:
			packet = gpsd.get_current()
			# latitude = latitude + .0005
			# longitude = longitude + .0005
			# print(packet.position())
			jsonReply['position'] = packet.position()
			jsonReply['time'] = packet.time()
			jsonReply['mapURL'] = packet.map_url()
			# jsonReply['time'] = str(datetime.now())
			# jsonReply['longitude'] = longitude
			# jsonReply['latitude'] = latitude
			reply = json.dumps(jsonReply)

		except Exception as e:
			print("Except: " + str(e))
			reply = "error"

		print(reply)

		ch.basic_publish(exchange='', 
						routing_key=props.reply_to,
						properties=pika.BasicProperties(correlation_id = \
						props.correlation_id),
						body=reply)
		ch.basic_ack(delivery_tag = method.delivery_tag)

if __name__ == '__main__':
	# setup GPS
	gpsd.connect()

	# Connect to RabbitMQ
	credentials = pika.PlainCredentials(username=username, password=password)
	connection =  pika.BlockingConnection(pika.ConnectionParameters(host=address,
																	port=port,
																	credentials=credentials))
	channel = connection.channel()
	channel.queue_declare(queue=queue_name)
	# Begin listening to queue
	channel.basic_qos(prefetch_count=1)
	channel.basic_consume(on_request, queue=queue_name)
	print(' [*] Waiting for messages. To exit press CTRL+C')
	# Start consuming messages
	channel.start_consuming()
	try:
		while True:
			sleep(2.5)
	except KeyboardInterrupt:
		channel.close()
		connection.close()