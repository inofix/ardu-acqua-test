#!/usr/bin/env python

import argparse
import json
import serial
import sys

def serial_read(device, baudrate):
    try:
        arduino_serial = serial.Serial(device, baudrate);

        result = {}
        data = ""

        while (True):
            if (arduino_serial.inWaiting() > 1):
                l = arduino_serial.readline()[:-2]

                if (l == "["):
                    # start recording
                    data = "["
                elif (l == "]") and (len(data) > 4) and (data[0] == "["):
                    print data
                    # now parse the input
                    data = data + "]"
                    j = json.loads(data)
## TODO: debug start
                    print ""
                    for v in j:
                        if v.has_key("unit"):
                            u = " " + v["unit"]
                        else:
                            u = ""
                        print v["name"] + " " + v["value"] + u
## TODO: debug end
                elif (l[0:3] == "  {"):
                    # this is a data line
                    data = data + " " + l

    except serial.serialutil.SerialException:
        print "Could not connect to the serial line at " + device

if __name__ == '__main__':

    cli_parser = argparse.ArgumentParser(description="Parse data from the arduino and use it for the Flussbad-Demo.")
    cli_parser.add_argument('-d', '--device', default='/dev/ttyACM1', help='serial device the arduino is connected to')
    cli_parser.add_argument('-b', '--baudrate', default=9600, help='baud rate of the serial line')
    args = cli_parser.parse_args()


    serial_read(args.device, args.baudrate)
