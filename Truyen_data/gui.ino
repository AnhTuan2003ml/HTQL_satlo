#include <SoftwareSerial.h>

SoftwareSerial hc12(D2, D3); // D2 = RX, D3 = TX 

#define LED_XANH D4

unsigned long lastSend = 0;

void setup() {
  Serial.begin(9600);    // Serial monitor
  hc12.begin(9600);      // HC-12 baudrate mặc định
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, HIGH); // Tắt LED (LED thường nối ngược)
}

void loop() {
  unsigned long now = millis();
  if (now - lastSend >= 1000) { // 1 giây
    String data = "t";
    hc12.println(data);
    Serial.print("Sent: ");
    Serial.println(data);
    digitalWrite(LED_BUILTIN, LOW);   // Bật LED
    delay(200);                    // Sáng 200ms
    digitalWrite(LED_BUILTIN, HIGH);  // Tắt LED
    lastSend = now;
  }
}
