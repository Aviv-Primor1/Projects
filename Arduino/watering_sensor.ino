int sensorPin = A0;
int ledPin = 13;
int sensorValue = 0;

void setup() {
  // put your setup code here, to run once:
Serial.begin(9600);
pinMode(ledPin, OUTPUT); 
}

void loop() {
  // put your main code here, to run repeatedly:
sensorValue = analogRead(sensorPin);
//sensorValue = map(sensorValue, 0, 1023, 255, 0);
Serial.println(sensorValue);
if (sensorValue > 700) {    // Soil is dry
    digitalWrite(ledPin, HIGH);  // Turn LED on
  } else {
    digitalWrite(ledPin, LOW);   // Turn LED off
  }
  delay(1000);
}
