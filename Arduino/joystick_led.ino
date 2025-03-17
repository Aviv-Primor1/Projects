// Arduino pin numbers
const int SW_pin = 2;  // digital pin connected to switch output
const int X_pin = 0;   // analog pin connected to X output
const int Y_pin = 1;   // analog pin connected to Y output

#define UP_LED 8
#define RIGHT_LED 9
#define LEFT_LED 10
#define DOWN_LED 11
#define BUZZER_PIN 12

void setup() {
  // put your setup code here, to run once:
  pinMode(SW_pin, INPUT);
  digitalWrite(SW_pin, HIGH);
  Serial.begin(115200);
  
  pinMode(UP_LED, OUTPUT);
  pinMode(RIGHT_LED, OUTPUT);
  pinMode(LEFT_LED, OUTPUT);
  pinMode(DOWN_LED, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  Serial.print("Switch: ");
  Serial.print(digitalRead(SW_pin));
  Serial.print("\\");
  Serial.print("X-axis: ");
  Serial.print(analogRead(X_pin));
  Serial.print("\\");
  Serial.print("Y-axis: ");
  Serial.println(analogRead(Y_pin));
  Serial.print("\\\\");
  delay(500);
  
  // Check joystick position and control LEDs and buzzer
  if(analogRead(X_pin) == 1023) {
    digitalWrite(UP_LED, HIGH);
    tone(BUZZER_PIN, 500, 100); // Higher pitch for up
  } 
  else if(analogRead(X_pin) == 0) {
    digitalWrite(DOWN_LED, HIGH);
    tone(BUZZER_PIN, 300, 100); // Lower pitch for down
  } 
  else if(analogRead(Y_pin) == 1023) {
    digitalWrite(RIGHT_LED, HIGH);
    tone(BUZZER_PIN, 600, 100); // Higher pitch for right
  } 
  else if(analogRead(Y_pin) == 0) {
    digitalWrite(LEFT_LED, HIGH);
    tone(BUZZER_PIN, 400, 100); // Medium pitch for left
  } 
  else if(digitalRead(SW_pin) == 0) {
    digitalWrite(UP_LED, HIGH);
    digitalWrite(LEFT_LED, HIGH);
    digitalWrite(RIGHT_LED, HIGH);
    digitalWrite(DOWN_LED, HIGH);
    // Play a little melody when button is pressed
    tone(BUZZER_PIN, 700, 50);
    delay(50);
    tone(BUZZER_PIN, 900, 50);
    delay(50);
    tone(BUZZER_PIN, 1100, 100);
  } 
  else {
    digitalWrite(UP_LED, LOW);
    digitalWrite(LEFT_LED, LOW);
    digitalWrite(RIGHT_LED, LOW);
    digitalWrite(DOWN_LED, LOW);
    // No sound when joystick is at rest
    noTone(BUZZER_PIN);
  }
}
