#include <OneWire.h>
#include <DallasTemperature.h>


// wait a second (or so..)
int timeout = 5000;

// install Photoresistor on
int lightPin = A0;
// install the 18B20 Temperature sensor on
int exactTempPin = 7;


// initialize the sensor variables
int lightValue = 0;

float exactTempValue = 0;

OneWire oneWire(exactTempPin);
DallasTemperature sensor(&oneWire);



void setup() {
    // Get a serial connection for reporting
    Serial.begin(9600);

    // initialize the temp sensor
    sensor.begin();
}

void loop() {
    // measure daylight
    lightValue = analogRead(lightPin);

    // measure temp.
    sensor.requestTemperatures();
    exactTempValue = sensor.getTempCByIndex(0);

    // All the serial output
    Serial.print("Light Value:");
    Serial.print(lightValue);
    Serial.println(";");

    Serial.print("Current exact Temperature: ");
    Serial.print(exactTempValue);
    Serial.println("C;");


    // sleep a little
    delay(timeout);
}

