#!/usr/bin/python3
import os
import sys
import subprocess
import json
import socket

listPay = []
namePayload = {}
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
    # print(encrypt)

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
    # Setup bluetooth
    bridgeMAC = '10:02:B5:3B:D4:C6'
    bridgePort = 25
    bridgeSocket = socket.socket(
        socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    bridgeSocket.connect((bridgeMAC, bridgePort))

    payloadJson = json.dumps(listPay)
    payloadSize = sys.getsizeof(payloadJson)
    #print(payloadJson)
    print(payloadSize)

    # Send json message
    result = bridgeSocket.sendall(bytes(payloadJson, "UTF-8"))
    print("Sent payload size: %s" % result)
    bridgeSocket.close()
def main():
    output = subprocess.check_output(
        "sudo iwlist wlan1 scanning", universal_newlines=True, shell=True)
    getAddr(output)
main()
