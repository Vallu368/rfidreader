#include <MFRC522.h>  // MFRC522 RFID module library.
#include <SPI.h>      // SPI device communication library.


#define RST_PIN 5      // Defines pins for RST, SS connections respectively.
#define SS_PIN 53

#define BUZZER_PIN 8   // Defines buzzer pin

#define RED_LED_PIN 9 // Define RGB LED pins
#define GREEN_LED_PIN 10
#define BLUE_LED_PIN 11

#define GREEN_BUTTON_PIN 18
#define RED_BUTTON_PIN 3

byte readCard[4];     // Array that will hold UID of the RFID card.
bool successRead;

MFRC522 mfrc522(SS_PIN, RST_PIN);   // Creates MFRC522 instance.

volatile int lastButtonPressed = 2; // 0: Red Button, 1: Green button, 2: No button/Error

void setup() {
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(RED_LED_PIN, OUTPUT);
  pinMode(GREEN_LED_PIN, OUTPUT);
  pinMode(BLUE_LED_PIN, OUTPUT);
  pinMode(GREEN_BUTTON_PIN, INPUT_PULLUP);
  pinMode(RED_BUTTON_PIN, INPUT_PULLUP);
  Serial.begin(9600); // Starts the serial connection at 9600 baud rate.
  SPI.begin();        // Initiates SPI connection between RFID module and Arduino.
  mfrc522.PCD_Init(); // Initiates MFRC522 RFID module.
  mfrc522.PCD_DumpVersionToSerial(); // Show details of RFID Reader, if version errors it isn't set up properly
  Serial.println("Please scan your RFID tag or card.");

  // Attach interrupts to the buttons
  attachInterrupt(digitalPinToInterrupt(GREEN_BUTTON_PIN), greenButtonINT, FALLING);
  attachInterrupt(digitalPinToInterrupt(RED_BUTTON_PIN), redButtonINT, FALLING);

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

    if (command == "BUZZ_ERROR") {
      BuzzError();
    }
    if (command == "BUZZ_GREEN") {
      BuzzGreen();
    }
    if (command == "BUZZ_BLUE") {
      BuzzBlue();
    }
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

  if (lastButtonPressed == 1) {
    Serial.print("1UID: ");
    BuzzGreen();
  } else if (lastButtonPressed == 0) {
    Serial.print("0UID: ");
    BuzzBlue();
  } else {
    Serial.print("2UID: ");
    BuzzError();
  }

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

void BuzzBlue() {
  digitalWrite(BLUE_LED_PIN, HIGH); // Turn the blue LED on
  digitalWrite(BUZZER_PIN, HIGH);  // Turn buzzer on
  delay(500);                      // Wait for half a second
  digitalWrite(BLUE_LED_PIN, LOW);  // Turn the blue LED off
  digitalWrite(BUZZER_PIN, LOW);   // Turn buzzer off
}


void BuzzGreen() {
  digitalWrite(GREEN_LED_PIN, HIGH); // Turn the green LED on
  digitalWrite(BUZZER_PIN, HIGH);    // Turn buzzer on
  delay(500);                        // Wait for half a second
  digitalWrite(GREEN_LED_PIN, LOW);  // Turn the green LED off
  digitalWrite(BUZZER_PIN, LOW);     // Turn buzzer off
}

void BuzzError() {
  digitalWrite(RED_LED_PIN, HIGH);
  digitalWrite(BUZZER_PIN, HIGH);
  delay(200);
  digitalWrite(RED_LED_PIN, LOW);
  digitalWrite(BUZZER_PIN, LOW);
  delay(200);
  digitalWrite(RED_LED_PIN, HIGH);
  digitalWrite(BUZZER_PIN, HIGH);
  delay(200);
  digitalWrite(RED_LED_PIN, LOW);
  digitalWrite(BUZZER_PIN, LOW);

}

void redButtonINT() {
  //Serial.println("RED button pressed");
  lastButtonPressed = 0; // Red button was pressed
  BuzzBlue();
}

void greenButtonINT() {
  //Serial.println("GREEN button pressed");
  lastButtonPressed = 1; // Green button was pressed
  BuzzGreen();
}
