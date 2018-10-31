#!/usr/bin/env python2
# Python script to retrieve and parse a DSMR telegram from a P1 port

import re
import sys
import serial
import crcmod.predefined
import datetime

# Debugging settings
production = True   # Use serial or file as input
debugging = 1   # Show extra output
# DSMR interesting codes
list_of_interesting_codes = {
    '1-0:1.8.1': 'Meter Reading electricity delivered to client (Tariff 1) in kWh',
    '1-0:1.8.2': 'Meter Reading electricity delivered to client (Tariff 2) in kWh',
    '1-0:2.8.1': 'Meter Reading electricity delivered by client (Tariff 1) in kWh',
    '1-0:2.8.2': 'Meter Reading electricity delivered by client (Tariff 2) in kWh',
    '0-0:96.14.0': 'Tariff indicator electricity',
    '1-0:1.7.0': 'Actual electricity power delivered (+P) in kW',
    '1-0:2.7.0': 'Actual electricity power received (-P) in kW',
    '0-0:17.0.0': 'The actual threshold electricity in kW',
    '0-0:96.3.10': 'Switch position electricity',
    '0-0:96.7.21': 'Number of power failures in any phase',
    '0-0:96.7.9': 'Number of long power failures in any phase',
    '1-0:32.32.0': 'Number of voltage sags in phase L1',
    '1-0:52.32.0': 'Number of voltage sags in phase L2',
    '1-0:72:32.0': 'Number of voltage sags in phase L3',
    '1-0:32.36.0': 'Number of voltage swells in phase L1',
    '1-0:52.36.0': 'Number of voltage swells in phase L2',
    '1-0:72.36.0': 'Number of voltage swells in phase L3',
    '1-0:31.7.0': 'Instantaneous current L1 in A',
    '1-0:51.7.0': 'Instantaneous current L2 in A',
    '1-0:71.7.0': 'Instantaneous current L3 in A',
    '1-0:21.7.0': 'Instantaneous active power L1 (+P) in kW',
    '1-0:41.7.0': 'Instantaneous active power L2 (+P) in kW',
    '1-0:61.7.0': 'Instantaneous active power L3 (+P) in kW',
    '1-0:22.7.0': 'Instantaneous active power L1 (-P) in kW',
    '1-0:42.7.0': 'Instantaneous active power L2 (-P) in kW',
    '1-0:62.7.0': 'Instantaneous active power L3 (-P) in kW'
}

# Program variables
# The true telegram ends with an exclamation mark after a CR/LF
pattern = re.compile(b'\r\n(?=!)')
# According to the DSMR spec, we need to check a CRC16
crc16 = crcmod.predefined.mkPredefinedCrcFun('crc16')
# Create an empty telegram
telegram = ''
checksum_found = False
good_checksum = False


if production:
    #Serial port configuration
    ser = serial.Serial()
    ser.baudrate = 115200
    ser.bytesize = serial.EIGHTBITS
    ser.parity = serial.PARITY_NONE
    ser.stopbits = serial.STOPBITS_ONE
    ser.xonxoff = 1
    ser.rtscts = 0
    ser.timeout = 12
    ser.port = "/dev/ttyUSB0"
else:
    print("Running in test mode")
    # Testing
    ser = open("raw.out", 'rb')

while True:
    try:
        # Read in all the lines until we find the checksum (line starting with an exclamation mark)
        if production:
            #Open serial port
            try:
                ser.open()
                telegram = ''
                checksum_found = False
            except Exception as ex:
                template = "An exception of type {0} occured. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                print message
                sys.exit("Fout bij het openen van %s. Programma afgebroken." % ser.name)
        else:
            telegram = ''
            checksum_found = False
        while not checksum_found:
            # Read in a line
            telegram_line = ser.readline()
            if debugging == 2:
                print(telegram_line.decode('ascii').strip())
            # Check if it matches the checksum line (! at start)
            if re.match(b'(?=!)', telegram_line):
                telegram = telegram + telegram_line
                if debugging:
                    print('Found checksum!')
                checksum_found = True
            else:
                telegram = telegram + telegram_line

    except Exception as ex:
        template = "An exception of type {0} occured. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print message
        print("There was a problem %s, continuing...") % ex
    #Close serial port
    if production:
        try:
            ser.close()
        except:
            sys.exit("Oops %s. Programma afgebroken." % ser.name)
    # We have a complete telegram, now we can process it.
    # Look for the checksum in the telegram
    for m in pattern.finditer(telegram):
        # Remove the exclamation mark from the checksum,
        # and make an integer out of it.
        given_checksum = int('0x' + telegram[m.end() + 1:].decode('ascii'), 16)
        # The exclamation mark is also part of the text to be CRC16'd
        calculated_checksum = crc16(telegram[:m.end() + 1])
        if given_checksum == calculated_checksum:
            good_checksum = True
    if good_checksum:
        if debugging == 1:
            print("Good checksum !")
        # Store the vaules in a dictionary
        telegram_values = dict()
        # Split the telegram into lines and iterate over them
        for telegram_line in telegram.split(b'\r\n'):
            # Split the OBIS code from the value
            # The lines with a OBIS code start with a number
            if re.match(b'\d', telegram_line):
                if debugging == 3:
                    print(telegram_line)
                # The values are enclosed with parenthesis
                # Find the location of the first opening parenthesis,
                # and store all split lines
                if debugging == 2:
                    print(telegram_line)
                if debugging == 3:
                    print re.split(b'(\()', telegram_line)
                # You can't put a list in a dict TODO better solution
                code = ''.join(re.split(b'(\()', telegram_line)[:1])
                value = ''.join(re.split(b'(\()', telegram_line)[1:])
                telegram_values[code] = value

        # Print the lines to screen
        for code, value in sorted(telegram_values.items()):
            if code in list_of_interesting_codes:
                # Cleanup value
                value = float(value.lstrip(b'\(').rstrip(b'\)*kWhA'))
                # Print nicely formatted string
		if debugging > 0:
			print(datetime.datetime.utcnow()), 
                print("{0:<63}{1:>12}".format(list_of_interesting_codes[code], value))
