#!/usr/bin/python3
import os
import subprocess
import json

listPay = []
namePayload= {}
dataPayload = {}

def getAddr(output):
	try:
		output = output.split("Address: ", 1)[1]
	except:
		convert2JSON(listPay)
		print("done")
		print("exiting")
		exit()
	else:
		address = output.split("\n", 1)[0]
		output = output.split("\n", 1)[1]
		#print ("address: ", address)

	output = output.split("Channel:", 1)[1]
	channel = output.split("\n", 1)[0]
	output = output.split("\n", 1)[1]
	#print ("Channel: ", channel)

	output = output.split("Frequency:", 1)[1]
	freq = output.split(" (", 1)[0]
	output = output.split(" (", 1)[1]
	#print ("Frequency: ", freq)

	output = output.split("Quality=", 1)[1]
	qualityFract = output.split(" ", 1)[0]
	output = output.split(" ", 1)[1]
	var = qualityFract.split("/")
	quality = int((float(var[0]) / float(var[1])) * 100.00)
	#print("Quality: ", quality)

	output = output.split("level=", 1)[1]
	signal = output.split(" \n", 1)[0]
	output = output.split(" \n", 1)[1]
	#print("Signal: ", signal)

	output = output.split(":", 1)[1]
	encrypt = output.split("\n", 1)[0]
	output = output.split("\n", 1)[1]
	#print(encrypt)

	output = output.split("\"", 1)[1]
	name = output.split("\"", 1)[0]
	output = output.split("\"", 1)[1]
	#output = output.split("ago\n", 1)[1]
	#print("Name: ", name)
	nextEntry(output, address, channel, freq, quality, signal, encrypt, name)



def nextEntry(output, address, channel, freq, quality, signal, encrypt, name):

	dataPayload['address'] = address
	dataPayload['channel'] = channel
	dataPayload['frequency'] = freq
	dataPayload['quality'] = quality
	dataPayload['signal'] = signal
	dataPayload['encryption'] = encrypt

	namePayload['name'] = name
	namePayload['data'] = dataPayload

	listPay.append(namePayload)

	getAddr(output)

def convert2JSON(listPay):
	payloadJson = json.dumps(listPay)
	print(payloadJson)

def main():

	output = subprocess.check_output("sudo iwlist wlan1 scanning", shell=True)
	getAddr(output)
main()

#python not python3
#monitor mode
#error