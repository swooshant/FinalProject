# -- Gps Pi code #
import gpsd
import json
import pika
import socket
import sys
import uuid
import time


# class gpsRPi(object):
	
	# def __init__(self, address, port, queue_name, username, password):

	#     self.queue_name = queue_name
	#     print("Setup Rabbitmq connection")
	#     #self.credentials = pika.PlainCredentials('team16', 'ece4564')
	#     #queue_name = 'brogrammers'

	#     #set the creditials and connection parameters for the message queue
	#     self.credentials = pika.PlainCredentials(username, password)
	#     self.connection = pika.BlockingConnection(pika.ConnectionParameters(address,
	#                                                                         port,
	#                                                                         '/',
	#                                                                         self.credentials))

	#     self.channel = self.connection.channel()
	#     result = self.channel.queue_declare(exclusive=True)
	#     self.callback_queue = result.method.queue

	#     self.channel.basic_consume(self.on_response, no_ack=True,
	#                                queue=self.callback_queue)
	# #queue callback
	# def on_response(self, ch, method, props, body):
	#     if self.corr_id == props.correlation_id:
	#     #the message queue will send an id back that is switched
	#         self.response = body

	# #this is called to push and pull to message queue
	# def call(self, gpsData):
	#     self.response = None
	#     self.corr_id = str(uuid.uuid4())
	#     self.channel.basic_publish(exchange='',
	#                                routing_key=self.queue_name,
	#                                properties=pika.BasicProperties(
	#                                    reply_to=self.callback_queue,
	#                                    correlation_id=self.corr_id),
	#                                body=gpsData)
	#     #break when all the messages are read for pull
	#     while self.response is None:
	#         self.connection.process_data_events()
	#     return self.response

	#  def getGpsInfo():
	#  	# Connect to the local gpsd
	# 	gpsd.connect()
	# 	packet = gpsd.get_current()
	# 	print(packet.position())

	 	# gpsData['lat'] = gpsd.fix.latitude
	 	# gpsData['long'] = gpsd.fix.longitude
	 	# gpsData['utc'] = gpsd.utc,' + ', gpsd.fix.time
	 	# gpsData['sats'] = gpsd.satellites


#message queue setup
# address = '172.31.61.87'
# port = 5672
# username = 'team16'
# password = 'ece4564'
# queue_name = 'brogrammers'

# # Setup rpc client
# gpsData = gpsRPi(address, port, queue_name, username, password)

# try:
while 1:
	try :
		gpsd.connect()
		packet = gpsd.get_current()
		print(packet.position())
		
	except Exception as e: 
		print("No fix found")
		print(e)
	time.sleep(5)
	      
# except KeyboardInterrupt:
#     print("Closing socket and channel")
#     s.close()
#     bridgeRPC.connection.close()

