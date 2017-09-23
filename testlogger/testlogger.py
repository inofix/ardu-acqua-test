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

from base64 import b64encode
import argparse
import datetime
import getpass
import json
import os
import re
import requests
import serial
import sys
import time
import threading
import urllib2

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
        # prepare a dict to store the data
        # this way we can wait for a stable set of values
        self.data = {}
        # remember the time of the last data update
        self.last_data_timestamp = None
        if re.match("file://", url):
            self.log = self.log_file
        elif re.match("https://", url) or re.match("http://", url):
            self.log = self.log_post
        else:
            self.log = self.log_stdout
        self.do_verify_certificate = True
        self.username = ""
        self.password = ""

    def register_json(self, data):
        """
        Register the contents as JSON
        """
        j = json.loads(data)

        for v in j:
            self.data[v["name"]] = v

        self.last_data_timestamp = datetime.datetime.utcnow().replace(microsecond=0).isoformat()

    def log_stdout(self):
        """
        Write to standard output
        """
        print "==== " + self.last_data_timestamp + " ===="
        for k in self.data:
            if self.data[k].has_key("unit"):
                u = " " + self.data[k]["unit"]
            else:
                u = ""
            print k + " " + self.data[k]["value"] + u

    def log_file(self):
        """
        Write to a local log file
        """
        pass

    def log_post(self):
        """
        Write to a remote host via HTTP POST
        """
        headers = {"Content-Type": "application/json"}
        try:
            request = requests.post(self.url, headers=headers, data=self.data, verify=self.do_verify_cerificate)
        except httplib.IncompleteRead as e:
            request = e.partial

    def log_ssh(self):
        """
        Write to a remote file via ssh
        """
        pass

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
            elif (mode == "report"):
                if logger.last_data_timestamp:
                    logger.log()
                else:
                    print "No data has been collected so far, please try again later.."
            else:
                print "This mode is not supported: " + mode
                print "Use one of 'start', 'stop', or 'exit' ..."


def get_credentials(args):
    """
    Helper function to get username and password
    """
    credentials = {}
    if args.user:
        credentials["user"] = args.user
    elif args.user_file:
        with open(args.user_file, "r") as of:
            pattern = re.compile("^user: ")
            for l in of:
                l = l[0:-1]
                if re.match(pattern, l):
                    credentials["user"] = re.sub(pattern, "", l)
    if credentials["user"][0:1] == '"' and credentials["user"][-1:] == '"':
        credentials["user"] = credentials["user"][1:-1]
    if args.password:
        credentials["password"] = getpass.getpass()
    elif args.password_file:
        with open(args.password_file, "r") as of:
            pattern = re.compile("^password: ")
            for l in of:
                l = l[0:-1]
                if re.match(pattern, l):
                    credentials["password"] = re.sub(pattern, "", l)
    if credentials["password"][0:1] == '"' and credentials["password"][-1:] == '"':
        credentials["password"] = credentials["password"][1:-1]

    # if both user and password is set,
    #  1. encode to base 64 for basic auth
    if credentials["user"] and credentials["password"]:
        credentials["base64"] = b64encode(credentials["user"] + ":" + credentials["password"]).decode("ascii")

def standard_mode(args):
    """
    Helper function to run for a certain amount of time
    """
    credentials = get_credentials(args)

    logger = DataLogger(args.target)

    reader = SerialReader(args.device, args.baudrate, logger, args.rounds)
    reader.start()
    time.sleep(args.seconds)
    reader.halt()
    logger.log()

if __name__ == '__main__':
    """
    Main function used if started on the command line
    """
    cli_parser = argparse.ArgumentParser(description="Parse data from the arduino and use it for the Flussbad-Demo.")
    cli_parser.add_argument('-b', '--baudrate', default=9600, help='baud rate of the serial line')
    cli_parser.add_argument('-d', '--device', default='/dev/ttyACM0', help='serial device the arduino is connected to')
    cli_parser.add_argument('-i', '--interactive', action="store_true", help='prompt for control and log to stdout')
    cli_parser.add_argument('-I', '--insecure', action="store_true", help='do not verify certificate on HTTPS POST')
    cli_parser.add_argument('-p', '--password', action="store_true", help='prompt for a password')
    cli_parser.add_argument('-P', '--password_file', default='', help='load password from this file, containing the line: \'password: "my secret text"\'')
    cli_parser.add_argument('-r', '--rounds', type=int, default=0, help='how many times to run the serial listener thread (default: 0 / infinite)')
    cli_parser.add_argument('-s', '--seconds', type=int, default=10, help='how long to run if not in interacitve mode')
    cli_parser.add_argument('-t', '--target', default="", help='target log, where to report the data to. Default is empty for <stdout>, the following URLs are provided yet: "file:///..", "http://..", "https://.."')
    cli_parser.add_argument('-u', '--user', default='', help='user name')
    cli_parser.add_argument('-U', '--user_file', default='', help='load user name from this file, containing the line: \'user: "my_name"\'')

    args = cli_parser.parse_args()

    if args.interactive:
        user_mode(args)
    else:
        standard_mode(args)
