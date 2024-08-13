# Arduino RFID Reader Project
This repository contains code for an RIFD Reader using Arduino, the Arduino sketch, and a tool to edit the SQL Database created for the RFID Reader

# RFID Reader
Requires an Arduino with an RC522 RFID Sensor and 2 buttons.
Once running, the program checks which button (In or Out) button has been pressed.
When the sensor scans an RFID Tag or Card, it checks if it is in the database, and if the tag/card has a name associated with it,  and either logs the person scanning in or out, or sends an error to the error log in the database.

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
