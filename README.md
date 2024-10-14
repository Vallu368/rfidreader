# Arduino RFID Reader Project
This repository contains code for an RIFD Reader using Arduino, the Arduino sketch, and a tool to edit the SQL Database created for the RFID Reader

# RFID Reader
The Purpose of the reader is to track traffic in the classroom.<br>
Requires an Arduino with an RC522 RFID Sensor and 2 buttons.<br>
Once running, the program waits for the Arduino to detect a card or a tag being scanned.<br>
After scanning a tag, the program will wait for a button top be pressed, to specify if you're either entering or leaving. If no button is pressed, the program will return to waiting for a scan.<br>
The Arduino is setup with a LCD screen, to give instructions to the user (Read Card, Press button, etc..), and to show if there is an error (Card not in database, trying to enter when already in, etc...)<br>

# SQL Database
The SQL Database is set in a way where all the tags/cards that the reader accepts, are in a table named "tags", while the names associated with each tag are in a table called "nicknames"<br>
"Access log" stores the information of every succesful log in/out<br>
"Action log" stores every action made by the rfidmanager<br>
"Error log" logs possible errors from the manager and reader (Tag not in database, etc..)<br>

# Arduino pins

## 16x2 LCD Screen
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
