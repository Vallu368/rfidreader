#include <MFRC522.h>  // MFRC522 RFID module library.
#include <SPI.h>      // SPI device communication library.
#include <LiquidCrystal.h>  // Library for LCD Screen


#define RST_PIN 49     // Defines pins for RST, SS connections respectively.
#define SS_PIN 53 

#define BUZZER_PIN 4   // Defines buzzer pin

#define RED_LED_PIN 10// Define RGB LED pins
#define GREEN_LED_PIN 8
#define BLUE_LED_PIN 9

#define GREEN_BUTTON_PIN 2
#define RED_BUTTON_PIN 3

#define LCD_BACKLIGHT_PIN 7 //Control backlight for powersaving
int Contrast=110; //Contrast set through arduino

LiquidCrystal lcd(12, 11, 25, 24, 23, 22); //pins for LCD data

int lcdCardCheck = 10;

byte readCard[4];     // Array that will hold UID of the RFID card.
bool successRead;

MFRC522 mfrc522(SS_PIN, RST_PIN);   // Creates MFRC522 instance.

volatile int lastButtonPressed = 2; // 0: Red Button, 1: Green button, 2: No button/Error

void setup() {
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(RED_LED_PIN, OUTPUT);
  pinMode(GREEN_LED_PIN, OUTPUT);
  pinMode(BLUE_LED_PIN, OUTPUT);
  pinMode(LCD_BACKLIGHT_PIN, OUTPUT);
  pinMode(GREEN_BUTTON_PIN, INPUT_PULLUP);
  pinMode(RED_BUTTON_PIN, INPUT_PULLUP);
  Serial.begin(9600); // Starts the serial connection at 9600 baud rate.
  SPI.begin();        // Initiates SPI connection between RFID module and Arduino.
  mfrc522.PCD_Init(); // Initiates MFRC522 RFID module.
  mfrc522.PCD_DumpVersionToSerial(); // Show details of RFID Reader, if version errors it isn't set up properly
  Serial.println("Please scan your RFID tag or card.");
  digitalWrite(7, LOW); //Backlight on
  analogWrite(6,Contrast);
  lcd.begin(16, 2);
  lcd.setCursor(0,0);
  lcd.print("Lue kortti ");
  

  // Attach interrupts to the buttons
  attachInterrupt(digitalPinToInterrupt(GREEN_BUTTON_PIN), greenButtonINT, FALLING);
  attachInterrupt(digitalPinToInterrupt(RED_BUTTON_PIN), redButtonINT, FALLING);

  // Wait for an RFID card to be presented before continuing
  do {
    successRead = getID(); // Loops getID function until reading process is done.
  } while (!successRead);
}

void loop() {

  if (lcdCardCheck == 1) { //button
    lcd.setCursor(0, 0);
    lcd.clear();
    lcd.print("Paina nappia  ");
  }
  else if (lcdCardCheck == 2) { //welcome
    lcd.setCursor(0, 0);
    lcd.clear();
    lcd.print("Tervetuloa!");
  }
  else if (lcdCardCheck == 3) { //Goodbye
    lcd.setCursor(0, 0);
    lcd.clear();
    lcd.print("Heippa!");
  }
  else if (lcdCardCheck == 0) { //Read Card
    lcd.setCursor(0,0);
    lcd.clear();
    lcd.print("Lue kortti");
  }
  else if (lcdCardCheck == 4) { //Not in database
    lcd.setCursor(0,0);
    lcd.clear();
    lcd.print("Ei tietokannassa!");
 
  }
  else if (lcdCardCheck == 5) { // already in
    lcd.setCursor(0,0);
    lcd.clear();
    lcd.print("Olet jo paikalla!");

  }
  else if (lcdCardCheck == 6) { //already out
    lcd.setCursor(0,0);
    lcd.clear();
    lcd.print("Olet jo ulkona! ");

  }
  else if (lcdCardCheck == 6) { //already out
    lcd.setCursor(0,0);
    lcd.clear();
    lcd.print("Et painanut nappia!  ");
  }

  
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
    if (command == "NAPPI") {
      LCDScreen(1);
    }
    if (command == "KORTTI") {
      LCDScreen(0);
    }
    if (command == "DATABASE") {
      LCDScreen(4);
    }
    if (command == "WELCOME") {
      LCDScreen(2);
    }
    if (command == "GOODBYE") {
      LCDScreen(3);
    }
    if (command == "DUPE") {
      LCDScreen(5);
    }
    if (command == "DUPEX") {
      LCDScreen(6);
    }
    if (command == "TIMEOUT") {
      LCDScreen(7);
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

  if (lastButtonPressed == 1) { //MADE REDUNDANT should be cleaned away
    Serial.print("1UID: ");
    BuzzBlue();
  } else if (lastButtonPressed == 0) {
    Serial.print("0UID: ");
    BuzzBlue();
  } else {
    Serial.print("2UID: ");
    BuzzBlue();
  }
  digitalWrite(7, HIGH);
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
  if (lastButtonPressed != 0) {
    lastButtonPressed = 0; // Red button was pressed
    Serial.println("0");
    BuzzBlue();
  }
}

void greenButtonINT() {
  //Serial.println("GREEN button pressed");
  if (lastButtonPressed != 1) {
    lastButtonPressed = 1; // Red button was pressed
    Serial.println("1");
    BuzzGreen();
  }
}

void LCDScreen(int i) {
  lcdCardCheck = i;
}
