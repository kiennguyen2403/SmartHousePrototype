// Includes the servo library
#include <Servo.h>.
// Defines Trig and Echo pins of the Ultrasonic Sensor
const int trigPin = 10;
const int echoPin = 11;
#define lightPin A0 // Defines the pin A0 as an output to lightPin
// Variables for the duration and the distance


long duration;
int distance;
int distanceThreshold = 20; // Distance threshold to turn on the light
int durationThreshold = 1000;

bool isPeopleDetected = false;


Servo myServo; // Creates a servo object for controlling the servo motor
void setup()
{
    pinMode(trigPin, OUTPUT); // Sets the trigPin as an Output
    pinMode(echoPin, INPUT);  // Sets the echoPin as an Input
    Serial.begin(9600);
    myServo.attach(12); // Defines on which pin is the servo motor attached
}
void loop()
{
    // rotates the servo motor from 15 to 165 degrees
    for (int i = 15; i <= 165; i++)
    {
        myServo.write(i);
        delay(30);
        distance = calculateDistance(); // Calls a function for calculating the distance measured by the Ultrasonic sensor for each degree
        if (distance < distanceThreshold)
        {
            // tone(lightPin, 10000 / distance); // Produces a different tone according to the distance the object is from the sensor
            digitalWrite(lightPin, HIGH); // Turns on the LED
        } 
    }
    // Repeats the previous lines from 165 to 15 degrees
    for (int i = 165; i > 15; i--)
    {
        myServo.write(i);
        delay(30);
        distance = calculateDistance();
        tone(lightPin, 10000 / distance); // Produces a different tone according to the distance the object is from the sensor
        if (distance < distanceThreshold)
        {
            // tone(lightPin, 10000 / distance); // Produces a different tone according to the distance the object is from the sensor
        }
    }
}
// Function for calculating the distance measured by the Ultrasonic sensor
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
