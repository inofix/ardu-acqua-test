#include <OneWire.h>
#include <DallasTemperature.h>
#include <DHT.h>

//// config ////

// wait a second (or so..)
int timeout = 2000;
// blink frequency
int blink = 500;

// install Photoresistor on
int lightPin = A0;
// install the 18B20 Temperature sensor on
int exactTempPin = 7;

// install Digital Humidity/Temperature sensor on
int dhtPin = 6;

// RGB warn led
int redWarnPin = 8;
int greenWarnPin = 9;
int blueWarnPin = 10;

// RGB led for brightness
int redBrightnessPin = 3;
int greenBrightnessPin = 4;
int blueBrightnessPin = 5;

int nightThreshold = 1000;
int nightValue = 1023;
int duskThreshold = 900;
int duskValue = 800;
int twilightThreshold = 500;
int twilightValue = 600;
int dayThreshold = 200;
int dayValue = 100;
int sunThreshold = 80;
int sunValue = 0;

//// init ////

// initialize the sensor variables
int lightValue = 0;

// 18B20
float exactTempValue = 0;
float warnTempThreshold = 30;

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

// brightness
int whiteValue = 0;

//// functions ////

void setup() {
    // Get a serial connection for reporting
    Serial.begin(9600);

    // initialize the temp sensor
    sensor.begin();

    // initialize the DHT
    dht.begin();

    // initialize the RGB warn LED
    pinMode(redWarnPin,OUTPUT);
    pinMode(greenWarnPin,OUTPUT);
    pinMode(blueWarnPin,OUTPUT);

    // initialize the second RGB LED, only white
    pinMode(redBrightnessPin,OUTPUT);
    pinMode(greenBrightnessPin,OUTPUT);
    pinMode(blueBrightnessPin,OUTPUT);
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

    if (exactTempValue > warnTempThreshold) {
        redValue = 255;
    }

    // serial user feedback
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

    analogWrite(redWarnPin, redValue);
    analogWrite(greenWarnPin, greenValue);
    analogWrite(blueWarnPin, blueValue);

    int ledLoop = timeout;

    if (lightValue < sunThreshold) {
        whiteValue = sunValue;
    } else if (lightValue < dayThreshold) {
        whiteValue = dayValue;
    } else if (lightValue < twilightThreshold) {
        whiteValue = twilightValue;
    } else if (lightValue < duskThreshold) {
        whiteValue = duskValue;
    } else {
        whiteValue = nightValue;
    }

    analogWrite(redBrightnessPin, whiteValue);
    analogWrite(greenBrightnessPin, whiteValue);
    analogWrite(blueBrightnessPin, whiteValue);

    // set the actors
    while (ledLoop > 0) {

        analogWrite(redWarnPin, redValue);
        analogWrite(greenWarnPin, greenValue);
        analogWrite(blueWarnPin, blueValue);
        delay(blink);
        analogWrite(redWarnPin, 0);
        analogWrite(greenWarnPin, 0);
        analogWrite(blueWarnPin, 0);
        delay(blink);
        ledLoop -= blink;
    }
}

