// install Photoresistor on A0
int lightPin = A0;
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
}

