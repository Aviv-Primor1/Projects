//Temperature and Humidity LCD Display
//Based on Elegoo examples

#include <LiquidCrystal.h>
#include <dht_nonblocking.h>

// DHT Sensor definitions
#define DHT_SENSOR_TYPE DHT_TYPE_11
static const int DHT_SENSOR_PIN = 2;
DHT_nonblocking dht_sensor(DHT_SENSOR_PIN, DHT_SENSOR_TYPE);

// LCD display pins
// LCD RS pin to digital pin 7
// LCD Enable pin to digital pin 8
// LCD D4 pin to digital pin 9
// LCD D5 pin to digital pin 10
// LCD D6 pin to digital pin 11
// LCD D7 pin to digital pin 12
LiquidCrystal lcd(7, 8, 9, 10, 11, 12);

void setup() {
  // Initialize serial port for debugging
  Serial.begin(9600);
  
  // Set up the LCD's number of columns and rows
  lcd.begin(16, 2);
  
  // Print initial message
  lcd.print("Temp & Humidity");
  lcd.setCursor(0, 1);
  lcd.print("Sensor starting");
  delay(2000);
}

// Poll for a measurement, keeping the state machine alive
static bool measure_environment(float *temperature, float *humidity) {
  static unsigned long measurement_timestamp = millis();
  
  // Measure once every three seconds
  if(millis() - measurement_timestamp > 3000ul) {
    if(dht_sensor.measure(temperature, humidity) == true) {
      measurement_timestamp = millis();
      return(true);
    }
  }
  return(false);
}

void loop() {
  float temperature;
  float humidity;
  
  // Measure temperature and humidity
  if(measure_environment(&temperature, &humidity) == true) {
    // Print to serial monitor for debugging
    Serial.print("T = ");
    Serial.print(temperature, 1);
    Serial.print(" deg. C, H = ");
    Serial.print(humidity, 1);
    Serial.println("%");
    
    // Clear the LCD and display new readings
    lcd.clear();
    
    // Display temperature on the first line
    lcd.setCursor(0, 0);
    lcd.print("Temp: ");
    lcd.print(temperature, 1);
    lcd.print(" C");
    
    // Display humidity on the second line
    lcd.setCursor(0, 1);
    lcd.print("Humidity: ");
    lcd.print(humidity, 1);
    lcd.print("%");
  }
}
