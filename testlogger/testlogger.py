#!/usr/bin/env python

import argparse
import serial
import sys


def serial_read(device, baudrate):
    try:
        arduino_serial = serial.Serial(device, baudrate);

        while (True):
            if (arduino_serial.inWaiting() > 1):
                data = arduino_serial.readline()
                print data

    except serial.serialutil.SerialException:
        print "Could not connect to the serial line at " + device

if __name__ == '__main__':

    cli_parser = argparse.ArgumentParser(description="Parse data from the arduino and use it for the Flussbad-Demo.")
    cli_parser.add_argument('-d', '--device', default='/dev/ttyACM1', help='serial device the arduino is connected to')
    cli_parser.add_argument('-b', '--baudrate', default=9600, help='baud rate of the serial line')
    args = cli_parser.parse_args()


    serial_read(args.device, args.baudrate)

