#include <Arduino.h>

#define LED_PIN 15

void setup() {
  Serial.begin(9600);
  Serial1.begin(9600, SERIAL_8N1, 16, 17); // RX=16 (RX2), TX=17 (TX2)
  pinMode(LED_PIN, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_PIN, LOW); // Tắt LED ban đầu
  digitalWrite(LED_BUILTIN, LOW); // Tắt LED tích hợp ban đầu
}

void loop() {
  if (Serial1.available()) {
    String received = Serial1.readStringUntil('\n');
    received.trim();
    Serial.print("Received: ");
    Serial.println(received);

    if (received == "t") {
      digitalWrite(LED_PIN, HIGH); // Bật LED ngoài
      digitalWrite(LED_BUILTIN, HIGH); // Bật LED tích hợp
      delay(200); // Sáng 200ms
      digitalWrite(LED_PIN, LOW);  // Tắt LED ngoài
      digitalWrite(LED_BUILTIN, LOW); // Tắt LED tích hợp
    }
  }
}
