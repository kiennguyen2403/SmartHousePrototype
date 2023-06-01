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
int MOVING_TIME = 4000;
unsigned long moveStartTime;
long duration = 0;
int distance = 0;
int distanceThreshold = 20; // Distance threshold to turn on the light
int durationThreshold = 1000;
unsigned long currentTime;
unsigned long startTime;
int distanceCurrent =0;

// state
int angle = 0;
int startAngle = 0;
int desiredAngle = 180;
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

  currentTime = millis() - startTime;

  Serial.println(
      "{\"angle\":" + String(angle) +
      ",\"distanceCurrent\":" + String(distanceCurrent) +
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
      moveStartTime = millis();
    }
    break;
  case TURN_OFF_SERVO:
    if (isServoRotate)
    {
      isServoRotate = false;
      myServo.write(0);
      startAngle = 0;
      desiredAngle = 180;
      angle = 0;
    }
    break;
  default:
    break;
  }

  digitalWrite(lightPin, isLightOn);

  if (isServoRotate)
  {
    if (moveStartTime < 0)
    {
      moveStartTime = millis();
    }
    unsigned long progress = millis() - moveStartTime;
  
    if (progress <= MOVING_TIME)
    {
      angle = map(progress, 0, MOVING_TIME -100, startAngle, desiredAngle);
      angle = constrain(angle, 0, 180);
      distanceCurrent = calculateDistance();
      myServo.write(angle);
      if (angle == desiredAngle && desiredAngle ==180){
        startAngle = 180;
        desiredAngle = 0;
        moveStartTime = millis();

      }
      else if (angle == desiredAngle && desiredAngle ==0){
        startAngle = 0;
        desiredAngle = 180;
        moveStartTime = millis();
      }
  
    }
    else if (angle != desiredAngle)
    {
      moveStartTime = millis();
    }
  }
  else
  {
    myServo.write(90);
    distanceCurrent = calculateDistance();
  }
}

void setup()
{
  

  pinMode(lightPin, OUTPUT);
  pinMode(trigPin, OUTPUT); // Sets the trigPin as an Output
  pinMode(echoPin, INPUT);  // Sets the echoPin as an Input
  Serial.begin(115200);
  myServo.attach(12); // Defines on which pin is the servo motor attached

  myServo.write(0);
  startAngle = 0;

  desiredAngle = 180;
  angle = 0;
  delay(1000);
  moveStartTime = millis();
  startTime = millis();
}

void loop()
{
  readData();
  deviceController();
  sendData();

  // rotates the servo motor from 15 to 165 degrees
}
// Function for calculating the distance measured by the Ultrasonic sensor
