#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <DHT_U.h>
#include <string.h>
#include <LiquidCrystal_I2C.h>
#define PIN_DHT11 3
#define PIN_FAN 4
#define PIN_HEATER 5
#define PIN_BUZZER 6
#define PIN_SMOKE A0

#define TURN_ON_FAN 0
#define TURN_OFF_FAN 1
#define TURN_ON_HEATER 2
#define TURN_OFF_HEATER 3
#define TURN_ON_BUZZER 4
#define TURN_OFF_BUZZER 5


DHT_Unified dht(PIN_DHT11, DHT11);

// Set the LCD address to 0x27 for a 16 chars and 2 line display
LiquidCrystal_I2C lcd(0x27, 16, 2);

// cached data
int temperature = 0;
int humidity = 0;
int smoke = 0;
bool fan = false;
bool heater = false;
bool buzzer = false;

volatile int interruptCounter = 0; // counter for the number of interrupts
volatile bool haveSent = false;

void setup() {
    // Use TIMER 2 because PWMServo uses TIMER 1
    // TIMER 2 for interrupt frequency 1000 Hz:
    cli(); // stop interrupts
    TCCR2A = 0; // set entire TCCR2A register to 0
    TCCR2B = 0; // same for TCCR2B
    TCNT2  = 0; // initialize counter value to 0
    // set compare match register for 1000 Hz increments
    OCR2A = 249; // = 16000000 / (64 * 1000) - 1 (must be <256)
    // turn on CTC mode
    TCCR2A |= (1 << WGM21);
    // Set CS22, CS21 and CS20 bits for 64 prescaler
    TCCR2B |= (1 << CS22) | (0 << CS21) | (0 << CS20);
    // enable timer compare interrupt
    TIMSK2 |= (1 << OCIE2A);
    sei(); // allow interrupts

    dht.begin();
    pinMode(PIN_SMOKE, INPUT);
    pinMode(PIN_FAN, OUTPUT);
    pinMode(PIN_HEATER, OUTPUT);
    pinMode(PIN_BUZZER, OUTPUT);

    Serial.begin(115200);

    lcd.begin();
	lcd.backlight();
	lcd.print("Awaiting data...");
}

ISR(TIMER2_COMPA_vect) {
    interruptCounter++;
    interruptCounter %= 5000;
    if (interruptCounter)
        haveSent = false;
}

void readSensors() {
    haveSent = true;
   
    sensors_event_t event;
    dht.temperature().getEvent(&event);
    if (isnan(event.temperature)) {
        Serial.println(F("Error reading temperature!"));
    }
    else {
        temperature = event.temperature;
    }
    dht.humidity().getEvent(&event);
    if (isnan(event.relative_humidity)) {
        Serial.println(F("Error reading humidity!"));
    }
    else {
        humidity = event.relative_humidity;
    }

    smoke = analogRead(PIN_SMOKE);

    display(
        "T: " + String(temperature) + "C",
        "H: " + String(humidity) + "%",
        "Fa: " + String((fan ? "ON" : "OFF")),
        "He: " + String((heater ? "ON" : "OFF"))
    );

    Serial.println(
        "{\"temperature\":" + String(temperature) +
        ",\"humidity\":" + String(humidity) +
        ",\"smoke\":" + String(smoke) +
        ",\"fan\":" + String((fan ? "true" : "false")) +
        ",\"heater\":" + String((heater ? "true" : "false")) +
        ",\"buzzer\":" + String((buzzer ? "true" : "false")) +"}"
    );
}

void display(String line1, String line2, String line3, String line4) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print(line1);
    lcd.setCursor(8, 0);
    lcd.print(line2);
    lcd.setCursor(0, 1);
    lcd.print(line3);
    lcd.setCursor(8, 1);
    lcd.print(line4);
}

void loop() {
    if (Serial.available() > 0) {
        int command = Serial.read() - '0';
        command = constrain(command, 0, 5);
        switch (command)
        {
        case TURN_ON_FAN:
            fan = true;
            break;
        case TURN_OFF_FAN:
            fan = false;
            break;
        case TURN_ON_HEATER:
            heater = true;
            break;
        case TURN_OFF_HEATER:
            heater = false;
            break;
        case TURN_ON_BUZZER:
            buzzer = true;
            break;
        case TURN_OFF_BUZZER:
            buzzer = false;
            break;
        default:
            break;
        }
    }

    digitalWrite(PIN_FAN, fan ? HIGH : LOW);
    digitalWrite(PIN_HEATER, heater ? HIGH : LOW);
    digitalWrite(PIN_BUZZER, buzzer ? HIGH : LOW);

    if (interruptCounter == 0 && !haveSent)
        readSensors();
}
