
//= includes =//

#include <OneWire.h>
#include <DallasTemperature.h>
#include <DHT.h>


//= config =//

//== set pins ==//

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

// Simple Iduino water sensor on pin
int waterLevelPin = A1;

// Ultrasonic water distance sensor HC-SR04 on pins
int triggerPin = 48;
int echoPin = 49;


//== control ==//

// wait a second (or so..)
int timeout = 1000;

// RGB brightness thresholds
int thresholdTolerancePercent = 10;
// reference value for threshold
int analogMax = 1023;

int nightThreshold = 1000;
int duskThreshold = 900;
int twilightThreshold = 500;
int dayThreshold = 200;
int sunThreshold = 80;

// RGB brightness values
int nightValue = 1023;
// TODO: why is 600 brighter than 800?
int duskValue = 800;
int twilightValue = 600;
int dayValue = 100;
int sunValue = 0;

// 18B20
float warnTempThreshold = 30;

// Iduino water conductivity (tested tap and salty water..)
int waterLevelThreshold = 600;

//== init ==//

// 18B20
OneWire oneWire(exactTempPin);
DallasTemperature sensor(&oneWire);

// DHT
DHT dht(dhtPin, DHT11);

// remember brightness
int lastLightValue = 0;
int whiteValue = 0;

//= functions =//

//== do once ==//

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

    // initialize the water level pin
    pinMode(waterLevelPin,INPUT);

    // initialize the HC-SR04
    pinMode(triggerPin,OUTPUT);
    pinMode(echoPin,INPUT);
}


//== main loop ==//

void loop() {

    //=== reset Pins ===//

    digitalWrite(triggerPin,LOW);


    //=== measurements ===//

    // measure daylight
    int lightValue = analogRead(lightPin);

    // measure water level
    int waterLevelValue = analogRead(waterLevelPin);

    // measure water distance
    digitalWrite(triggerPin,HIGH);
    delayMicroseconds(1);
    digitalWrite(triggerPin,LOW);
    int waterDistanceDuration = pulseIn(echoPin,HIGH);
    // calc half the way and in (almost) centimeters ..
    int waterDistanceValue = waterDistanceDuration / 2 / 34;

    // measure temp.
    sensor.requestTemperatures();
    float exactTempValue = sensor.getTempCByIndex(0);

    // measure humidity and temp.
    float envTempValue = dht.readTemperature();
    float envHumidityValue = dht.readHumidity();
    float heatIndex = 0;
    if (isnan(envHumidityValue) || isnan(envTempValue)) {
        Serial.println("Error reading environment data.");
    } else {
        heatIndex = dht.computeHeatIndex(envTempValue, envHumidityValue, false);
    }

    int redValue = 0;
    int greenValue = 0;
    int blueValue = 0;

    if (exactTempValue > warnTempThreshold) {
        redValue = 255;
    }

    if (waterLevelValue > waterLevelThreshold) {
        blueValue = 255;
    }

    //=== serial user feedback ===//

    Serial.print("Light Value Index: ");
    Serial.println(lightValue);

    Serial.print("Box Temperature (°C): ");
    Serial.println(exactTempValue);

    // DHT
    Serial.print("Environment Temperature (°C): ");
    Serial.println(envTempValue);
    Serial.print("Environment Humidity (%): ");
    Serial.println(envHumidityValue);
    Serial.print("Calculated Heat Index: ");
    Serial.println(heatIndex);

    Serial.print("Water Contact: ");
    Serial.println(waterLevelValue);

    Serial.print("Water Distance (mm): ");
    Serial.println(waterDistanceValue);
    Serial.println("========================================");

    //=== set the actors ===//

    analogWrite(redWarnPin, redValue);
    analogWrite(greenWarnPin, greenValue);
    analogWrite(blueWarnPin, blueValue);

    if (abs(lastLightValue - lightValue) >
            analogMax / thresholdTolerancePercent) {
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

    analogWrite(redWarnPin, redValue);
    analogWrite(greenWarnPin, 0);
    analogWrite(blueWarnPin, 0);
    delay(timeout / 3);

    analogWrite(redWarnPin, 0);
    analogWrite(greenWarnPin, greenValue);
    analogWrite(blueWarnPin, 0);
    delay(timeout / 3);

    analogWrite(redWarnPin, 0);
    analogWrite(greenWarnPin, 0);
    analogWrite(blueWarnPin, blueValue);
    delay(timeout / 3);

    analogWrite(redWarnPin, 0);
    analogWrite(greenWarnPin, 0);
    analogWrite(blueWarnPin, 0);
}

