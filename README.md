# Arduino RFID Reader Project
This repository contains code for an RIFD Reader using Arduino, the Arduino sketch, and a tool to edit the SQL Database created for the RFID Reader

# RFID Reader
The Purpose of the reader is to track traffic in the classroom.<br>
Requires an Arduino with an RC522 RFID Sensor and 2 buttons.<br>
Once running, the program waits for the Arduino to detect a card or a tag being scanned.<br>
After scanning a tag, the program will wait for a button top be pressed, to specify if you're either entering or leaving. If no button is pressed, the program will return to waiting for a scan.<br>
The Arduino is setup with a LCD screen, to give instructions to the user (Read Card, Press button, etc..), and to show if there is an error (Card not in database, trying to enter when already in, etc...)<br>

# RFID Manager
This tool was made to make managing the database easier, and without needing to access the phpmyadmin site.<br>
This tool can: <br>

Show all tags/cards in the database, their ID, and associated name if they have one<br>

- Add a new name to an existing tag in the database<br>

- Remove a name from an existing tag with a name already assigned to it<br>

- Add a new tag or card into the database<br>

- Read succesful scans<br>

- Read the error log<br>

- Read the action log (Every action done from the RFID Manager)<br>

- Log out everyone currently logged in through the scanner for debugging purposes<br>

This tool does not require an Arduino with an RC522 RFID Sensor for anything other than adding new cards or tags into the database<br>

To use the tool, launch it from command prompt with the command "python rfidmanager.py", or use the executable.<br>

# SQL Database
The SQL Database is set in a way where all the tags/cards that the reader accepts, are in a table named "tags", while the names associated with each tag are in a table called "nicknames"<br>
"Access log" stores the information of every succesful log in/out<br>
"Action log" stores every action made by the rfidmanager<br>
"Error log" logs possible errors from the manager and reader (Tag not in database, etc..)<br>

# Arduino
This project was made using an Arduino Mega 2560 Rev3 / JOY-iT MEGA 2560 and the following parts:<br>
1x RGB LED light<br>
2x Button<br>
1x Arduino Piezo<br>
1x RFID-RFC522 module<br>
1x 16x2 LCD Screen<br>
## 16x2 LCD Screen
The LCD Screen is set in a way where you can change the wanted contrast using the Arduino Sketch, instead of a potentiometer<br>
## 16x2 LCD Screen Pins
VSS to GND<br>
VDD to 5V<br>
V0 to Digital pin 4<br>
RS to Digital Pin 25<br>
RW to GND <br>
E to Digital Pin 27 <br>
<br>
D4 to Digital Pin 29<br>
D5 to Digital Pin 31 <br>
D6 to Digital Pin 33 <br>
D7 to Digital Pin 35 <br>
A to Digital Pin 37 <br>
K to GND <br>

## RFID-RFC522 Module Pins
SDA to Digital Pin 46<br>
SCK to Digital Pin 52<br>
MOSI to Digital Pin 51<br>
MISO to Digital Pin 50<br>
RST to Digital Pin 49<br>

## Button Pins
In Button to Digital Pin 2<br>
Out Button to Digital Pin 3<br>

## RGB LED Pins
R to Digital Pin 10<br>
B to Digital Pin 9<br>
G to Digital Pin 8<br>