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


//stayr

bool isPeopleDetected = false;
bool isServoRotate = false;
bool isLightOn = false;

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

void sendData(){
  String distanceListStringPrevious = "[";
  for (int i =0; i < 90; i++){
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

void readData(){
  if (Serial.available())
  {
    command = Serial.read() - '0';
    command = constrain(command, 0, 3);
  }
}

void deviceController(){

  switch (command)
  {
    case TURN_ON_LIGHT:
      isLightOn = true;
      currentTime = 0;
      break;
    case TURN_OFF_LIGHT:
      isLightOn = false;
      currentTime = 0;
      break;
    case TURN_ON_SERVO:
      isServoRotate = true;
      break;
    case TURN_OFF_SERVO:
      isServoRotate = false;
      break;
    default:
      isLightOn = false;
      break;
  }

  digitalWrite(lightPin, isLightOn);

  if (isServoRotate)
  {
          for (int i = 0; i <= 90; i += 1) {
            myServo.write(i);
            distance = calculateDistance();
            distanceListPrevious[i] = distance;
          }
          for (int i = 90; i >= 0; i -= 1) {
            myServo.write(i);
            distance = calculateDistance();
            distanceListCurrent[i] = distance;
           
          }
        } else {
            myServo.write(90);
            distance = calculateDistance();
            distanceListPrevious[90] = distance;
            int distance2 = calculateDistance();
            distanceListCurrent[90] = distance2;
        }
  }

void setup()
{
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
  sendData();
    // rotates the servo motor from 15 to 165 degrees   
}
// Function for calculating the distance measured by the Ultrasonic sensor

