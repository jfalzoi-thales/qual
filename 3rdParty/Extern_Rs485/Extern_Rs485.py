import serial
import argparse
import logging

from common.logger.logger import Logger
cmdParameters = argparse.ArgumentParser(description="Runs the external application to be used by RS2485 Modeule")
cmdParameters.add_argument('port',
                           type= str,
                           default= '/dev/ttyUSB5',
                           help= "Port")
cmdParameters.add_argument('baudrate',
                           type= int,
                           default= 115200,
                           help= "Baud Rate")
## Parse the command line arguments
args = cmdParameters.parse_args()

## Logger
log = Logger(name="RS-485 External application", level=logging.DEBUG)

serialPort = serial.Serial(port=args.port,
                           baudrate=args.baudrate,
                           parity=serial.PARITY_NONE,
                           stopbits=serial.STOPBITS_ONE,
                           bytesize=serial.EIGHTBITS,
                           timeout=3)

log.info("Started...")
while True:
    rX = serialPort.read()
    if len(rX) > 0:
        log.info("Data received: %s <--" % (rX,))
        serialPort.write(rX)
        log.info("Data sent:     %s -->" % (rX,))