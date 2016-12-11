#!/usr/bin/python3
import os
import sys
import subprocess
import json
import socket

# list of the data Payloads
listPay = []
namePayload = {}
dataPayload = {}

# Fucntion that gets all of the required data
def getAddr(output):
	# See if there is another network we need to find
    try:
    	# If there is, get the address
        output = output.split("Address: ", 1)[1]
    except:
    	# Otherwise, convert the payload to a JSON
        convert2JSON(listPay)
        print("done")
        print("exiting")
        exit()
    else:
    	# Grab the address
        address = output.split("\n", 1)[0]
        output = output.split("\n", 1)[1]
        #print ("address: ", address)

    #split the output at channel, grab the channel and update the variable
    output = output.split("Channel:", 1)[1]
    channel = output.split("\n", 1)[0]
    output = output.split("\n", 1)[1]

    #split the output at Frequency, grab the Frequency and update the variable
    output = output.split("Frequency:", 1)[1]
    freq = output.split(" (", 1)[0]
    output = output.split(" (", 1)[1]

    output = output.split("Quality=", 1)[1]
    qualityFract = output.split(" ", 1)[0]
    output = output.split(" ", 1)[1]
    var = qualityFract.split("/")
    quality = int((float(var[0]) / float(var[1])) * 100.00)

    #split the output at signal, grab the signal strength and update the variable
    output = output.split("level=", 1)[1]
    signal = output.split(" \n", 1)[0]
    output = output.split(" \n", 1)[1]

    #split the output at encryption, grab the encryption type and update the variable
    output = output.split(":", 1)[1]
    encrypt = output.split("\n", 1)[0]
    output = output.split("\n", 1)[1]
    # print(encrypt)

    #split the output at name, grab the network name and update the variable
    output = output.split("\"", 1)[1]
    name = output.split("\"", 1)[0]
    output = output.split("\"", 1)[1]

    # Push the variables to the send function
    nextEntry(output, address, channel, freq, quality, signal, encrypt, name)

# Creates the JSON package and sends it
def nextEntry(output, address, channel, freq, quality, signal, encrypt, name):

	# Puts the following in the data payload
    dataPayload['address'] = address
    dataPayload['channel'] = channel
    dataPayload['frequency'] = freq
    dataPayload['quality'] = quality
    dataPayload['signal'] = signal
    dataPayload['encryption'] = encrypt

    # Loads the name and data payload in the name payload
    namePayload['name'] = name
    namePayload['data'] = dataPayload

    # appends this payload to the list
    listPay.append(namePayload)

    # See if there is another network available
    getAddr(output)


def convert2JSON(listPay):
    # Setup bluetooth
    bridgeMAC = '10:02:B5:3B:D4:C6'
    bridgePort = 25
    bridgeSocket = socket.socket(
        socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    bridgeSocket.connect((bridgeMAC, bridgePort))

    # converts list to json
    payloadJson = json.dumps(listPay)
    # find the length of the payload
    payloadSize = sys.getsizeof(payloadJson)

    print(payloadSize)

    # Send json message
    result = bridgeSocket.sendall(bytes(payloadJson, "UTF-8"))
    print("Sent payload size: %s" % result)
    bridgeSocket.close()

# main    
def main():
	#call the scan command
    output = subprocess.check_output(
        "sudo iwlist wlan1 scanning", universal_newlines=True, shell=True)
    getAddr(output)
main()
