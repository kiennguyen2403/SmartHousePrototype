// Includes the servo library
#include <Servo.h>

#define TURN_ON_LIGHT 0
#define TURN_OFF_LIGHT 1
#define TURN_ON_SERVO 2
#define TURN_OFF_SERVO 3
// Defines Trig and Echo pins of the Ultrasonic Sensor
const int trigPin = 10;
const int echoPin = 11;
const int lightPin = 13; //

int command = 5;

long duration = 0;
int distance = 0;
int distanceThreshold = 20; // Distance threshold to turn on the light
int durationThreshold = 1000;
unsigned long currentTime;
unsigned long startTime;
int distanceListPrevious[91];
int distanceListCurrent[91];

// state

bool isPeopleDetected = false;
bool isServoRotate = true;
bool isLightOn = false;
volatile int interruptCounter = 0; // counter for the number of interrupts
volatile bool haveSent = false;

Servo myServo; // Creates a servo object for controlling the servo motor

int calculateDistance()
{
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  // Sets the trigPin on HIGH state for 10 micro seconds
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  duration = pulseIn(echoPin, HIGH); // Reads the echoPin, returns the sound wave travel time in microseconds
  distance = duration * 0.034 / 2;
  return distance;
}

void sendData()
{
  String distanceListStringPrevious = "[";
  for (int i = 0; i < 90; i++)
  {
    distanceListStringPrevious += String(distanceListPrevious[i]) + ",";
  }
  distanceListStringPrevious += String(distanceListPrevious[90]);
  distanceListStringPrevious += "]";

  String distanceListStringCurrent = "[";
  for (int i = 0; i < 90; i++)
  {
    distanceListStringCurrent += String(distanceListCurrent[i]) + ",";
  }
  distanceListStringCurrent += String(distanceListCurrent[90]);
  distanceListStringCurrent += "]";
  currentTime = millis() - startTime;

  Serial.println(
      "{\"distancePrevious\":" + distanceListStringPrevious +
      ",\"distanceCurrent\":" + distanceListStringCurrent +
      ",\"timer\":" + String(currentTime) +
      ",\"light\":" + String(isLightOn) +
      ",\"servo\":" + String(isServoRotate) + "}");
}

void readData()
{
  if (Serial.available())
  {
    command = Serial.read() - '0';
    command = constrain(command, 0, 3);
  }
}

void deviceController()
{

  switch (command)
  {
  case TURN_ON_LIGHT:
    if (!isLightOn)
    {
      startTime = millis();
      isLightOn = true;
      
    }
    break;
  case TURN_OFF_LIGHT:
    if (isLightOn)
    {
      isLightOn = false;
      startTime = millis();
    }
    break;
  case TURN_ON_SERVO:
    if (!isServoRotate)
    {
      isServoRotate = true;
    }
    break;
  case TURN_OFF_SERVO:
    if (isServoRotate)
    {
      isServoRotate = false;
    }
    break;
  default:
    break;
  }

  digitalWrite(lightPin, isLightOn);

  if (isServoRotate)
  {
    for (int i = 0; i <= 90; i += 5)
    {
      myServo.write(i);

      distanceListPrevious[i] = calculateDistance();
    }
    for (int i = 90; i >= 0; i -= 5)
    {
      myServo.write(i);
      distanceListCurrent[i] = calculateDistance();
    }
  }
  else
  {
    myServo.write(90);
    distanceListPrevious[90] = calculateDistance();
    delay(100);
    distanceListCurrent[90] = calculateDistance();
  }
}

ISR(TIMER2_COMPA_vect)
{
  interruptCounter++;

  if (interruptCounter > 1000)
  {
    interruptCounter = 0;
    haveSent = false;
  }
}

void setup()
{
  cli();      // stop interrupts
  TCCR2A = 0; // set entire TCCR2A register to 0
  TCCR2B = 0; // same for TCCR2B
  TCNT2 = 0;  // initialize counter value to 0
  // set compare match register for 1000 Hz increments
  OCR2A = 249; // = 16000000 / (64 * 1000) - 1 (must be <256)
  // turn on CTC mode
  TCCR2A |= (1 << WGM21);
  // Set CS22, CS21 and CS20 bits for 64 prescaler
  TCCR2B |= (1 << CS22) | (0 << CS21) | (0 << CS20);
  // enable timer compare interrupt
  TIMSK2 |= (1 << OCIE2A);
  sei(); // allow interrupts

  pinMode(lightPin, OUTPUT);
  pinMode(trigPin, OUTPUT); // Sets the trigPin as an Output
  pinMode(echoPin, INPUT);  // Sets the echoPin as an Input
  Serial.begin(115200);
  myServo.attach(12); // Defines on which pin is the servo motor attached
  myServo.write(90);
  startTime = millis();
}
void loop()
{
  readData();
  deviceController();
  
  if (!haveSent)
  {
    sendData();
    haveSent = true;
  }

  

  // rotates the servo motor from 15 to 165 degrees
}
// Function for calculating the distance measured by the Ultrasonic sensor
