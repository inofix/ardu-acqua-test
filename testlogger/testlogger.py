#!/usr/bin/env python

import serial
import sys


def serial_read(device, baudrate):
    try:
        arduino_serial = serial.Serial(device, baudrate);

        while (True):
            if (arduino_serial.inWaiting() > 1):
                data = arduino_serial.readline()
                print data

    except:
        print "Could not connect to the serial line at" + device + " " + \
            baudrate

if __name__ == '__main__':

    serial_read('/dev/ttyACM1', 9600)

