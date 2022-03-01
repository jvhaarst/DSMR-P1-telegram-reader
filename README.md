DSMR-P1-telegram-reader
=======================

Python program to read Dutch Smart Meter Requirements (DSMR) telegrams from a serial port 
connected to the P1 port of a smart meter, and print it on screen or push it to another site.

There are different branches, the master just pretty prints the data, the xively branch adds pushing to xively.

Installation
============

Just do ```git clone``` in a directory of choice.
You might need to change the settings of the serial port, and/or change the permissions of the port.

Usage
=====

To run, first install needed python modules:
```
virtualenv --python=python3 venv3;
source venv3/bin/activate;
pip install -r requirements.txt;
```

After that you can run the program with ```./telegram_from_serial.py```.

Notes
=====

The specification and a list of OBIS codes from the specification can be found in the documentation folder.
