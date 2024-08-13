# Arduino RFID Reader Project
This repository contains code for an RIFD Reader using Arduino, the Arduino sketch, and a tool to edit the SQL Database created for the RFID Reader

# RFID Reader
The Purpose of the reader is to keep track of traffic  in the classroom.
Requires an Arduino with an RC522 RFID Sensor and 2 buttons.
Once running, the program checks which button (In or Out) button has been pressed.
If you can see the console, there will be text once you scan a tag, something like "0/1/2UID: XXXXXX"
the number in front of "UID" is for keeping track of what button was pressed, as in if the person is going in or out (1 means in, 2 out, 0 no button pressed)
When the sensor scans an RFID Tag or Card, it reads its UID, and checks if it is in the database. If UID isn't in the database, it sends out an error.

# RFID Manager
This tool was made to make managing the database easier, and without needing to access the phpmyadmin site.

This tool can: 
- Show all tags/cards in the database, their ID, and associated name if they have one

- Add a new name to an existing tag in the database

- Remove a name from an existing tag with a name already assigned to it

- Add a new tag or card into the database

- Read succesful scans

- Read the error log

- Read the action log (Everything action done from the RFID Manager)

- Log out everyone currently logged in through the scanner for debugging purposes


This tool does not require an Arduino with an RC522 RFID Sensor for anything other than adding new cards or tags into the database

To use the tool, launch it from command prompt with the command "python rfidmanager.py", or use the executable.

# Arduino & Arduino Sketch

This project was made using an Arduino Mega 2560 Rev3 / JOY-iT MEGA 2560 and the following parts:
1x RGB LED light
2x button
1x Arduino Piezo
1x RFID-RFC522 module

The Pins used are:
RFID-RFC522 SDA - Arduino 5
RFID-RFC522 SCK - Arduino 51
RFID-RFC522 MOSI - Arduino 49
RFID-RFC522 MISO - Arduino 48
RFID-RFC522 RST - Arduino 8 

RGB LED Red - Arduino 9
RGB LED Green - Arduino 10
RGB LED Blue - Arduino 11

In Button - Arduino 18
Out button - Arduino 3

# SQL Database
This project uses an SQL Database setup in the following way:
Database: rfid
Tables - Structure:
action_log - id(int), date(varchar), action(varchar)
error_log - id(int), date(varchar), tag_uid(varchar), error_type(varchar)
latka - id(int), rfid_uid(varchar)
nicknames - latka_id(int), nick(varchar)
rfid_data - id(int), date(varchar), uid(varchar), in_out(int)

Action log documents any action taken using the RFID Manager with the current time of action and what action was done

Error log logs anything causing an error, such as failure to login (tag/card not in database, logging in when already in, etc). The error shows the UID of the tag/card responsible for the error, when the error happened, and what type of an error it was.

latka (lätkä is finnish for tag) holds all the tags or cards in the database, and their UID.

nicknames is for all the tags/cards currently in use. It holds the id from latka table, and the name of the current user of that tag/card.

rfid_data holds all the successful scans of the RFID Module.

# Usage

Reader:

Download and use the Arduino IDE to upload the included sketch onto your Arduino, if using different pin locations make sure to change them in the Arduino sketch

Set up your Database tables as shown earlier, if you change the names of anything, make sure you change them in BOTH rfidmanager.py and rfidreader.py

Setup the correct mysql connection parameters in both rfidmanager.py and rfidreader.py

Connect your Arduino with the sketch uploaded to the machine you want to run the scanner, and launch rfidreader.py

Manager:

Launch the rfidmanager.py script either by using the console (python rfidmanager.py) or by using the executable included


