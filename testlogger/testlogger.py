#!/usr/bin/env python

"""
PURPOSE:      read the serial output of one or more arduino boards
              and store the sensor values..
DEPENDENCY:   python 2.7
PLATTFORM:    currently only unix/linux is supported
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

    def __init__(self, url):
        """
        Initialize the data logger
            url url      URL to send the data to
        """
        self.data = []
        self.url = url

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

    def __init__(self, device, baudrate, logger, rounds):
        """
        Initialize the serial reader class
            device        device name to connect to
            baudrate      the baud rate for the serial line
            logger        the logger object to send the data to
            rounds        number of rounds to run / listen for input
        """
        threading.Thread.__init__(self)
        self.device = device
        self.baudrate = baudrate
        self.logger = logger
        self.rounds = rounds
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
                        # now parse the input
                        data = data + "]"
                        self.logger.register_json(data)
                        if self.rounds == 1:
                            self.do_run = False
                        elif self.rounds > 1:
                            self.rounds -= 1
                    elif (l[0:3] == "  {"):
                        # this is a data line
                        data = data + " " + l

        except serial.serialutil.SerialException:
            print "Could not connect to the serial line at " + self.device

    def halt(self):
        """
        Tell the logger to stop working after the next round
        """
        self.do_run = False

def user_mode(args):
    """
    Helper function to run in interactive mode
    """
    logger = DataLogger("")

    # hold a dict of serial connections
    threads = {}

    print "Welcome to the interactive mode!"
    print "You have the following options:"
    print "    register [device] [baud]         add a device to observe"
    print "    unregister [device]              remove a device"
    print "    rounds num                       number of rounds to run threads"
    print "    exit                             cleanup and quit"

    # set the default number of rounds to run a thread from the CLI
    rounds = args.rounds

    while True:

        # prompt for user input
        sys.stdout.write(":-> ")
        sys.stdout.flush()

        # get user input
        m = os.read(0,80)[:-1]

        # prepare the modes
        ms = m.split(" ")
        mode = ms[0]

        # standard values from the CLI
        device = args.device
        device_name = re.sub("/dev/", "", args.device)
        baudrate = args.baudrate

        # now do what the user wants - part 1
        if (mode == "rounds" and len(ms) > 1):
            rounds = int(ms[1])
        elif (mode == "exit" or mode == "quit"):
            # clean up
            i = iter(threads)
            for k in i:
                t = threads[k]
                t.halt()
            # and exit
            return
        else:
            # if the device is specified, set it
            if len(ms) > 1:
                if ms[1][0:1] == "/":
                    device = ms[1]
                    device_name = ms[1].sub("/dev/", "", args.device)
                else:
                    device = "/dev/" + ms[1]
                    device_name = ms[1]

            # if device and baudrate are specified, also set the baudrate
            if len(ms) > 2:
                baudrate = ms[2]

            # now do what the user wants
            if (mode == "register"):
                if threads.has_key(device_name):
                    print "This device was already registered"
                else:
                    # create an object that connects to the serial line
                    threads[device_name] = SerialReader(device, baudrate, logger, rounds)
                    # start recording
                    threads[device_name].start()
            elif (mode == "unregister"):
                if threads.has_key(device_name) and isinstance(threads[device_name], SerialReader):
                    # end the recording and remove the device from the list
                    threads[device_name].halt()
                    threads.pop(device_name)
            else:
                print "This mode is not supported: " + mode
                print "Use one of 'start', 'stop', or 'exit' ..."

def standard_mode(args):
    """
    Helper function to run for a certain amount of time
    """
    logger = DataLogger("")

    thread = SerialReader(args.device, args.baudrate, logger, args.rounds)
    thread.start()
    time.sleep(args.seconds)
    thread.halt()

if __name__ == '__main__':
    """
    Main function used if started on the command line
    """
    cli_parser = argparse.ArgumentParser(description="Parse data from the arduino and use it for the Flussbad-Demo.")
    cli_parser.add_argument('-d', '--device', default='/dev/ttyACM0', help='serial device the arduino is connected to')
    cli_parser.add_argument('-b', '--baudrate', default=9600, help='baud rate of the serial line')
    cli_parser.add_argument('-i', '--interactive', action="store_true", help='prompt for control')
    cli_parser.add_argument('-s', '--seconds', type=int, default=10, help='how long to run if not in interacitve mode')
    cli_parser.add_argument('-r', '--rounds', type=int, default=0, help='how many times to run the serial listener thread (default: 0 / infinite)')
    args = cli_parser.parse_args()

    if args.interactive:
        user_mode(args)
    else:
        standard_mode(args)
