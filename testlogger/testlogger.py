#!/usr/bin/env python

import argparse
import json
import os
import re
import serial
import sys
import time
import threading

class DataLogger(object):

    def __init__(self):
        self.data = []

    def register_json(self, data):
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

class SerialReader(threading.Thread):

    def __init__(self, device, baudrate, logger):
        threading.Thread.__init__(self)
        self.device = device
        self.baudrate = baudrate
        self.logger = logger
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
                        self.logger.register_json(data)
                    elif (l[0:3] == "  {"):
                        # this is a data line
                        data = data + " " + l

        except serial.serialutil.SerialException:
            print "Could not connect to the serial line at " + device

    def halt(self):
        self.do_run = False

def user_mode(args):

    logger = DataLogger()

    # just one thread for now..

    # one arduino is enough for the moment, but..
    device_name = re.sub("/dev/", "", args.device);
    threads = {}

    while True:

        sys.stdout.write(":-> ")
        sys.stdout.flush()
        mode = os.read(0,10)[:-1]

        if (mode == "start"):
            threads[device_name] = SerialReader(args.device, args.baudrate, logger)
            threads[device_name].start()
        elif (mode == "stop"):
            if threads.has_key(device_name) and isinstance(threads[device_name], SerialReader):
                threads[device_name].halt()
        elif (mode == "exit" or mode == "quit"):
            return
        else:
            print "This mode is not supported:" + mode
            print "Use one of 'start', 'stop', or 'exit' ..."

if __name__ == '__main__':

    cli_parser = argparse.ArgumentParser(description="Parse data from the arduino and use it for the Flussbad-Demo.")
    cli_parser.add_argument('-d', '--device', default='/dev/ttyACM1', help='serial device the arduino is connected to')
    cli_parser.add_argument('-b', '--baudrate', default=9600, help='baud rate of the serial line')
    cli_parser.add_argument('-i', '--interactive', action="store_true", help='prompt for control')
    cli_parser.add_argument('-s', '--seconds', type=int, default=10, help='how long to run if not in interacitve mode')
    args = cli_parser.parse_args()

    if args.interactive:
        user_mode(args)
    else:
        logger = DataLogger()
        thread = SerialReader(args.device, args.baudrate, logger)
        thread.start()
        time.sleep(args.seconds)
        thread.halt()

