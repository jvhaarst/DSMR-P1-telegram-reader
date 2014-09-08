DSMR-P1-telegram-reader
=======================

Python program to read Dutch Smart Meter Requirements (DSMR) telegrams from a serial port 
connected to the P1 port of a smart meter, and print it on screen or push it to another site.

Installation
============

Just do ```git clone``` in a directory of choice.
You might need to change the settings of the serial port, and/or change the permissions of the port.

Usage
=====

To run, first install needed python modules:
```
virtualenv --python=python2 venv2;
source venv2/bin/activate;
pip install -r requirements.txt;
```

After that you can run the program with ```telegram_from_serial.py```.

Xively
======

To run in Xively mode, checkout this branch, and run it like this :
```FEED_ID=feed_number API_KEY=api_key_of_feed ./telegram_from_serial.py```

Notes
=====

The specification and a list of OBIS codes from the specification can be found in the documentation folder.
