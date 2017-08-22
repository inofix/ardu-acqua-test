
// wait a second (or so..)
int timeout = 1000;

// install Photoresistor on A0
int lightPin = A0;





// initialize the light variable
int lightValue = 0;





void setup() {
    Serial.begin(9600);
}

void loop() {
    // measure daylight
    lightValue = analogRead(lightPin);

    Serial.print("Light Value:");
    Serial.print(lightValue);
    Serial.println(";");

    delay(timeout);
}

