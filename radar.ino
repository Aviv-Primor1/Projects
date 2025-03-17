#include <Servo.h>
#include "SR04.h"


const int servoPin= 9;
const int triggerPin = 12;
const int echoPin = 11;
const int buzzerPin = 8;

Servo myservo;
SR04 mySensor = SR04(echoPin,  triggerPin);
long distance; 

//epBuzzer();

void setup() {
  // put your setup code here, to run once:
myservo.attach(servoPin);
Serial.begin(9600);
pinMode(buzzerPin, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
for(int i=0; i<= 180; i++) 
  {
     myservo.write(i);
     delay(20);
      distance = mySensor.Distance();
      Serial.print(distance);
      Serial.println("cm");
      if(distance <= 5)
     {
      int beepInterval = map(distance, 5, 0, 50, 1);
      beepBuzzer(beepInterval);
     }
  }
for(int i=180; i>= 0; i--) 
  {
     myservo.write(i);
     delay(20);
     distance = mySensor.Distance();
     Serial.print(distance);
     Serial.println("cm");
     if(distance <= 5)
     {
      int beepInterval = map(distance, 5, 0, 50, 1);
      beepBuzzer(beepInterval);
     }
  }
}


void beepBuzzer(int beepInterval)
{
  digitalWrite(buzzerPin, HIGH);
  delay(beepInterval);
  digitalWrite(buzzerPin, LOW);
  delay(1);
  
}
