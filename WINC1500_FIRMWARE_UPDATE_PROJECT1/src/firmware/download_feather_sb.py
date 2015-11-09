#!/usr/bin/python

import sys
import glob
import serial
import argparse
import time
import os
import re
import subprocess
import sys
import time
import uuid

HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'


def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


if __name__ == '__main__':
    starttime = time.time()
    # Parse the input arguments
    argparser = argparse.ArgumentParser(description="Programs and tests a Feather M0 Basic")
    argparser.add_argument("hexfile", help="hex file for serial bridge", default=False)
    argparser.add_argument("zeroport", help="native serial port location for zero ('COM14', '/dev/tty.usbserial-DN009WNO')", default=False)

    argparser.add_argument("-v", "--verbose", dest="verbose", action="store_true", default=False,
                           help="verbose mode (all serial traffic is displayed)")
    args = argparser.parse_args()

    startingports = serial_ports()
    print(startingports)

  # reset 
    ser = serial.Serial(args.zeroport, 1200, timeout=1)
    time.sleep(1);
    ser.close();
    time.sleep(3);


    endingports = serial_ports()
    print(endingports)

    for p in startingports:
       endingports.remove(p)
  
    print(endingports)
    if (len(endingports) > 0):
        bootport = endingports[0]
    else:
        bootport = args.zeroport
    
  # program the Feather M0 serial bridge
    print (HEADER+"Programming serial bridge...."+ENDC)
    ret = ""
    try:
        ret = subprocess.check_output(["Tools/bossac", "-i", "-d", "--port="+bootport, "-U", "true",  "-i", "-e", "-w", "-v", args.hexfile, "-R"], stderr=subprocess.STDOUT)
    except:
        print ret
    	print FAIL+"Failed to talk to chip, bootloader ok?"+ENDC

    if (not "Verify 59744 bytes of flash with checksum." in ret) or (not "Verify successful" in ret):
    	print FAIL+"bossac returned ", ret+ENDC
    	exit(1)

    if args.verbose:
        print ret

    print OKGREEN+"Programmed" , ENDC

    exit(0)


