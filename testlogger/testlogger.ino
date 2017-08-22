#include <OneWire.h>
#include <DallasTemperature.h>
#include <DHT.h>


//// config ////

// wait a second (or so..)
int timeout = 5000;

// install Photoresistor on
int lightPin = A0;
// install the 18B20 Temperature sensor on
int exactTempPin = 7;

// install Digital Humidity/Temperature sensor on
int dhtPin = 6;

// RGB warn led
int redPin = 8;
int greenPin = 9;
int bluePin = 10;


//// init ////

// initialize the sensor variables
int lightValue = 0;

// 18B20
float exactTempValue = 0;

// DHT
float envTempValue = 0;
float envHumidityValue = 0;
float heatIndex = 0;

// 18B20
OneWire oneWire(exactTempPin);
DallasTemperature sensor(&oneWire);

// DHT
DHT dht(dhtPin, DHT11);

// PWM value for the colors
int redValue = 0;
int greenValue = 0;
int blueValue = 0;


//// functions ////

void setup() {
    // Get a serial connection for reporting
    Serial.begin(9600);

    // initialize the temp sensor
    sensor.begin();

    // initialize the DHT
    dht.begin();

    // initialize the RGB warn led
    pinMode(redPin,OUTPUT);
    pinMode(greenPin,OUTPUT);
    pinMode(bluePin,OUTPUT);
}

void loop() {
    // measure daylight
    lightValue = analogRead(lightPin);

    // measure temp.
    sensor.requestTemperatures();
    exactTempValue = sensor.getTempCByIndex(0);

    // measure humidity and temp.
    envTempValue = dht.readTemperature();
    envHumidityValue = dht.readHumidity();
    if (isnan(envHumidityValue) || isnan(envTempValue)) {
        Serial.println("Error reading environment data.");
    } else {
        heatIndex = dht.computeHeatIndex(envTempValue, envHumidityValue, false);
    }

    redValue = 0;
    greenValue = 0;
    blueValue = 0;

    if (exactTempValue > 30) {
        redValue = 255;
    }

    // All the serial output
    Serial.print("Light Value:");
    Serial.print(lightValue);
    Serial.println(";");

    Serial.print("Current exact Temperature: ");
    Serial.print(exactTempValue);
    Serial.println("C;");

    Serial.print("Humidity: ");
    Serial.print(envHumidityValue);
    Serial.print("%; Temperature: ");
    Serial.print(envTempValue);
    Serial.print("C; Heat Index: ");
    Serial.print(heatIndex);
    Serial.println(";");

    analogWrite(redPin, redValue);
    analogWrite(greenPin, greenValue);
    analogWrite(bluePin, blueValue);

    // sleep a little
    delay(timeout);
}

