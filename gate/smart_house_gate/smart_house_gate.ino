
#include <SPI.h>
#include <MFRC522.h>      //MFRC522 library by Miki Balboa
#include <ArduinoJson.h>  //ArduinoJson library by Benoit Blanchon
#include <Servo.h>
#include <Ultrasonic.h>         // Ultrasonic library by Erick Simoes
#include <LiquidCrystal_I2C.h>  // LiquidCrystal I2C library by Frank de Brabander
#include "DHT.h"

#define BUZZER_PIN 4
#define DHTPIN 7   
#define DHTTYPE DHT11   // DHT 11
#define RST_PIN 9
#define SS_PIN 10
#define TRIG_PIN 6
#define ECHO_PIN 5
#define SERVO_PIN 8
#define PASSWORD_BLOCK 53

LiquidCrystal_I2C lcd(0x27, 20, 4);
Ultrasonic ultrasonic(TRIG_PIN, ECHO_PIN);
StaticJsonDocument<200> doc;
MFRC522 mfrc522(SS_PIN, RST_PIN);
Servo servo1;
int numberOfSlot;  // The number of available parking slots in the parking area.
int waterVal = 0;
DHT dht(DHTPIN, DHTTYPE);
bool buzzer_state = false;

void setup() {
  Serial.begin(9600);
  SPI.begin();
  lcd.init();
  lcd.backlight();
  mfrc522.PCD_Init();
  servo1.attach(SERVO_PIN);
  servo1.write(0);
  lcd.clear();
  dht.begin();
  pinMode(BUZZER_PIN,OUTPUT);
}


bool readData(byte blockNumber, byte buffer1[]) {
  // This function reads the data on the blockNumber of the Mifare card and copy the data into a buffer
  // blockNumber: The block number on the Mifare card
  // buffer1: The buffer that the data will be copied into
  MFRC522::MIFARE_Key key;
  for (byte i = 0; i < 6; i++) key.keyByte[i] = 0xFF;
  MFRC522::StatusCode status;
  byte len = 18;

  status = mfrc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, blockNumber, &key, &(mfrc522.uid));  // authenticate
  if (status != MFRC522::STATUS_OK) {
    return false;
  }

  status = mfrc522.MIFARE_Read(blockNumber, buffer1, &len);  // read the data on the blockNumber and copy the data into buffer
  if (status != MFRC522::STATUS_OK) {
    return false;
  }

  return true;
}


void loop() {
  doc.clear();
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  lcd.setCursor(0, 0);
  lcd.print("                   ");
  lcd.setCursor(0, 0);
  lcd.print("T:" + String(t));
  lcd.setCursor(9, 0);
  lcd.print("H:" + String(h));   // Display the number of available slots on the screen
  int distance = ultrasonic.read();
  if (distance <= 10) {
    doc["direction"] = "out";
    serializeJson(doc, Serial);  // Send the data to Serial line
    Serial.println();
    delay(2000);
  }
  if (buzzer_state) {
    digitalWrite(BUZZER_PIN,HIGH);
  } else {
    digitalWrite(BUZZER_PIN,LOW);
  }
  
  if (Serial.available() > 0) {                               // Read from the serial line
    String json= Serial.readString();
    // a.trim();
    deserializeJson(doc, json);
    const char* method = doc["method"];
    if (doc["method"] == "OpenGate") {
      servo1.write(90);  // Open the gate if it receive command "open"
      delay(2000);       // Hold the gate for 2 seconds
      servo1.write(0);   // Close the gate
    } else if (doc["method"] == "UpdateWeather") {
      lcd.setCursor(0, 1);
      String rainValue = doc["value"];
      lcd.print("Rain: " + rainValue); 
    } else if (doc["method"] = "setValueBuzzer") {
      buzzer_state = doc["params"];
    }
  }


  if (!mfrc522.PICC_IsNewCardPresent()) {  // If the RFID reader detects a Mifare card
    return;
  }


  if (!mfrc522.PICC_ReadCardSerial()) {
    return;
  }


  byte passwordBuffer[18];



  if (readData(PASSWORD_BLOCK, passwordBuffer)) {  // Read Customer name, Customer ID, and password


    String password;
    for (uint8_t i = 0; i < 16; i++) {

      password += char(passwordBuffer[i]);
    }
    password.trim();

    // Serializing the data into JSON format
    doc["password"] = password;
    doc["direction"] = "in";
    serializeJson(doc, Serial);  // Send the data to Serial line
    Serial.println();
  }


  mfrc522.PICC_HaltA();  // Stop reading the card
  mfrc522.PCD_StopCrypto1();
}