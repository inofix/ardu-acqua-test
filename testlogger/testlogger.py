#!/usr/bin/env python

"""
PURPOSE:      read the serial output of one or more arduino boards
              and store the sensor values..
AUTHOR(S):    michael lustenberger inofix.ch
COPYRIGHT:    (C) 2017 by Michael Lustenberger and INOFIX GmbH

              This program is free software under the GNU General Public
              License (>=v2).
"""

import argparse
import json
import os
import re
import serial
import sys
import time
import threading

class DataLogger(object):
    """
    Logger class for parsing a data string and log the contents
    """

    def __init__(self):
        """
        Initialize the data logger
        """
        self.data = []

    def register_json(self, data):
        """
        Register the contents as JSON
        """
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
    """
    Reader class for connecting to an end device and reading its output
    """

    def __init__(self, device, baudrate, logger):
        """
        Initialize the serial reader class
        """
        threading.Thread.__init__(self)
        self.device = device
        self.baudrate = baudrate
        self.logger = logger
        self.do_run = True

    def run(self):
        """
        Open a connection over the serial line and receive data lines
        """
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
        """
        Tell the logger to stop working after the next round
        """
        self.do_run = False

def user_mode(args):
    """
    Helper function to run in interactive mode
    """
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

def standard_mode(args):
    """
    Helper function to run for a certain amount of time
    """
    logger = DataLogger()
    thread = SerialReader(args.device, args.baudrate, logger)
    thread.start()
    time.sleep(args.seconds)
    thread.halt()

if __name__ == '__main__':
    """
    Main function used if started on the command line
    """
    cli_parser = argparse.ArgumentParser(description="Parse data from the arduino and use it for the Flussbad-Demo.")
    cli_parser.add_argument('-d', '--device', default='/dev/ttyACM1', help='serial device the arduino is connected to')
    cli_parser.add_argument('-b', '--baudrate', default=9600, help='baud rate of the serial line')
    cli_parser.add_argument('-i', '--interactive', action="store_true", help='prompt for control')
    cli_parser.add_argument('-s', '--seconds', type=int, default=10, help='how long to run if not in interacitve mode')
    args = cli_parser.parse_args()

    if args.interactive:
        user_mode(args)
    else:
        standard_mode(args)
