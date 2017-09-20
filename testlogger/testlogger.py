#!/usr/bin/env python

import argparse
import json
import os
import re
import serial
import sys
import time
import threading

class SerialReader(threading.Thread):

    def __init__(self, device, baudrate):
        threading.Thread.__init__(self)
        self.device = device
        self.baudrate = baudrate
        self.do_run = True

    def run(self):
        try:
            arduino_serial = serial.Serial(self.device, self.baudrate);

            data = ""

            while (self.do_run):
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

def user_mode(args):

    # just one thread for now..

    # one arduino is enough for the moment, but..
    device_name = re.sub("/dev/", "", args.device);
    threads = {}

    while True:

        sys.stdout.write(":-> ")
        sys.stdout.flush()
        mode = os.read(0,10)[:-1]

        if (mode == "start"):
            threads[device_name] = SerialReader(args.device, args.baudrate)
            threads[device_name].start()
        elif (mode == "stop"):
            if threads.has_key(device_name) and isinstance(threads[device_name], SerialReader):
                threads[device_name].do_run = False
        elif (mode == "exit" or mode == "quit"):
            return
        else:
            print "..." + mode + "..."

if __name__ == '__main__':

    cli_parser = argparse.ArgumentParser(description="Parse data from the arduino and use it for the Flussbad-Demo.")
    cli_parser.add_argument('-d', '--device', default='/dev/ttyACM1', help='serial device the arduino is connected to')
    cli_parser.add_argument('-b', '--baudrate', default=9600, help='baud rate of the serial line')
    args = cli_parser.parse_args()

    user_mode(args)

