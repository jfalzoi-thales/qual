import serial
import argparse
import random


cmdParameters = argparse.ArgumentParser(description="Runs the external application to be used by RS2485 Modeule")
cmdParameters.add_argument('-p',
                           dest='port',
                           type= str,
                           default= '/dev/ttyUSB0',
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

try:
    serialPort = serial.Serial(port=args.port,
                               baudrate=args.baudrate,
                               parity=serial.PARITY_NONE,
                               stopbits=serial.STOPBITS_ONE,
                               bytesize=serial.EIGHTBITS,
                               timeout=3)
except serial.SerialException:
    print("Unable to initialize device %s" % (args.port,))
else:
    count = 0
    print("Device %s started..." % (args.port,))
    while True:
        rX = serialPort.read()
        if len(rX) > 0:
            if args.mismatches and count % 5 == 0:
                rX = chr(random.randint(0,255))
                serialPort.write(rX)
            else:
                serialPort.write(rX)
        count += 1