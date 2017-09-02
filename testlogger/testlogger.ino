#include <OneWire.h>
#include <DallasTemperature.h>
#include <DHT.h>

//// config ////

/// set pins

// install Photoresistor on pin
int lightPin = A0;

// install the 18B20 Temperature sensor on pin
int exactTempPin = 7;

// install Digital Humidity/Temperature sensor on pin
int dhtPin = 6;

// RGB warn led on pins
int redWarnPin = 8;
int greenWarnPin = 9;
int blueWarnPin = 10;

// RGB led for brightness on pins
int redBrightnessPin = 3;
int greenBrightnessPin = 4;
int blueBrightnessPin = 5;

// Relay for the big water pump on pin
int pumpPin = 46;

// Simple water sensor on pin
int waterLevelPin = A1;

// Ultrasonic water distance sensor HC-SR04 on pins
int triggerPin = 48;
int echoPin = 49;

/// control

// wait a second (or so..)
int timeout = 2000;

// blink frequency
int blink = 500;

// RGB brightness thresholds
int thresholdTolerancePercent = 10;
int nightThreshold = 1000;
int duskThreshold = 900;
int twilightThreshold = 500;
int dayThreshold = 200;
int sunThreshold = 80;

// RGB brightness values
int nightValue = 1023;
// TODO: why is 600 brighter than 800?
int duskValue = 600;
int twilightValue = 800;
int dayValue = 100;
int sunValue = 0;


//// init ////

// initialize the sensor/actor variables
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
int lastLightValue = 0;
int whiteValue = 0;

// water level
int waterLevelValue = 0;

// water distance
long waterDistanceValue = 0;
long waterDistanceDuration = 0;

//// functions ////

void setup() {
    // Get a serial connection for reporting
    Serial.begin(9600);

    // initialize photoresistor
    pinMode(lightPin,INPUT);

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

    // initialize the pump
    pinMode(pumpPin,OUTPUT);

    // initialize the HC-SR04
    pinMode(triggerPin,OUTPUT);
    pinMode(echoPin,INPUT);
}

void loop() {

    //// init ////

    // reset Pins
    digitalWrite(triggerPin,LOW);



    //// measurements ////

    // measure daylight
    lightValue = analogRead(lightPin);

    // measure water level
    waterLevelValue = analogRead(waterLevelPin);

    // measure water distance
    digitalWrite(triggerPin,HIGH);
    delayMicroseconds(1);
    digitalWrite(triggerPin,LOW);
    waterDistanceDuration = pulseIn(echoPin,HIGH);
    // half the way
    waterDistanceValue = waterDistanceDuration / 2;
    // almost centimeters ...
    waterDistanceValue = waterDistanceValue / 34;

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

    //// serial user feedback ////
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

    Serial.print("Water Level: ");
    Serial.print(waterLevelValue);
    Serial.println(";");

    Serial.print("Water Distance: ");
    Serial.print(waterDistanceValue);
    Serial.println(";");

    analogWrite(redWarnPin, redValue);
    analogWrite(greenWarnPin, greenValue);
    analogWrite(blueWarnPin, blueValue);

    int ledLoop = timeout;

    if (abs(lastLightValue - lightValue) >
            lightValue / thresholdTolerancePercent) {
        lastLightValue = lightValue;
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

