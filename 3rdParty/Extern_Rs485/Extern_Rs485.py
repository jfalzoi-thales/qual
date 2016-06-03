import serial
import argparse
import logging
import random

from common.logger.logger import Logger

cmdParameters = argparse.ArgumentParser(description="Runs the external application to be used by RS2485 Modeule")
cmdParameters.add_argument('-p',
                           dest='port',
                           type= str,
                           default= '/dev/ttyUSB5',
                           help= "Port")
cmdParameters.add_argument('-b',
                           dest='baudrate',
                           type= int,
                           default= 115200,
                           help= "Baud Rate")
cmdParameters.add_argument('-m',
                           dest='mismatches',
                           action="store_true",
                           help= "Send some corrupted data")
## Parse the command line arguments
args = cmdParameters.parse_args()

## Logger
log = Logger(name="RS-485 External application", level=logging.DEBUG)

try:
    serialPort = serial.Serial(port=args.port,
                               baudrate=args.baudrate,
                               parity=serial.PARITY_NONE,
                               stopbits=serial.STOPBITS_ONE,
                               bytesize=serial.EIGHTBITS,
                               timeout=3)
except serial.SerialException:
    log.info("Unable to initialize device %s" % (args.port,))
else:
    count = 0
    log.info("Device %s started..." % (args.port,))
    while True:
        rX = serialPort.read()
        if len(rX) > 0:
            log.info("Data received: %s <--" % (rX,))
            if args.mismatches and count % 5 == 0:
                rX = chr(random.randint(0,255))
                serialPort.write(rX)
            else:
                serialPort.write(rX)
            log.info("Data sent:     %s -->" % (rX,))
        count += 1