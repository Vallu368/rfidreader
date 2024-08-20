#include <MFRC522.h>  // MFRC522 RFID module library.
#include <SPI.h>      // SPI device communication library.


#define RST_PIN 5      // Defines pins for RST, SS connections respectively.
#define SS_PIN 53

byte readCard[4];     // Array that will hold UID of the RFID card.
bool successRead;

MFRC522 mfrc522(SS_PIN, RST_PIN);   // Creates MFRC522 instance.

volatile int lastButtonPressed = 2; // 0: Red Button, 1: Green button, 2: No button/Error

void setup() {
  Serial.begin(9600); // Starts the serial connection at 9600 baud rate.
  SPI.begin();        // Initiates SPI connection between RFID module and Arduino.
  mfrc522.PCD_Init(); // Initiates MFRC522 RFID module.
  mfrc522.PCD_DumpVersionToSerial(); // Show details of RFID Reader, if version errors it isn't set up properly
  Serial.println("Please scan your RFID tag or card.");

  // Wait for an RFID card to be presented before continuing
  do {
    successRead = getID(); // Loops getID function until reading process is done.
  } while (!successRead);
}

void loop() {
  getID(); // Continuously check for new RFID cards
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim(); // Remove any trailing whitespace or newline characters
  }
}

bool getID() {
  // Check if a new card is present
  if (!mfrc522.PICC_IsNewCardPresent()) {
    return false;
  }

  // Select one of the cards
  if (!mfrc522.PICC_ReadCardSerial()) {
    return false;
  }
  Serial.print("0UID: ");
  String UID = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    readCard[i] = mfrc522.uid.uidByte[i]; // Reads RFID card's UID
    UID += String(readCard[i], HEX); // Save UID as string for database
  }

  Serial.println(UID);
  mfrc522.PICC_HaltA(); // Halt the PICC

  // Reset the button pressed status after handling
  lastButtonPressed = 2;

  return true;
}
