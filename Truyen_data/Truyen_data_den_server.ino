// Thư viện cần thiết cho WiFi và HTTP (ESP8266) - Phiên bản cuối
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClientSecure.h>
#include <time.h>

// Thông tin WiFi - thay đổi theo mạng WiFi của bạn
const char* ssid = "CMCC-TshH";        // Tên mạng WiFi
const char* password = "bzyz3779"; // Mật khẩu WiFi

// Cấu hình Firebase
const char* firebaseUrl = "https://quanlyrung-d69ec-default-rtdb.firebaseio.com/";
const char* authToken = "ZHlyXYQXhJBHH76oHdtdXlYs9kth3eCwFzdAPvku";

// Biến điều khiển
unsigned long lastSendTime = 0;                    // Thời điểm gửi dữ liệu cuối cùng
const unsigned long sendInterval = 600000;          // Gửi dữ liệu mỗi 1 tiếng (600000ms)

void setup() {
  Serial.begin(115200);
  Serial.println();
  Serial.println("Ket noi WiFi...");
  
  // Kết nối WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println();
  Serial.println("Da ket noi WiFi thanh cong!");
  Serial.print("Dia chi IP: ");
  Serial.println(WiFi.localIP());
  
  // Cấu hình NTP server
  Serial.println("Dong bo thoi gian NTP...");
  configTime(7 * 3600, 0, "pool.ntp.org", "time.nist.gov");
  
  // Chờ đồng bộ thời gian
  time_t now = time(nullptr);
  int waitCount = 0;
  while (now < 100000 && waitCount < 30) {
    delay(1000);
    now = time(nullptr);
    waitCount++;
    Serial.print(".");
  }
  
  if (now > 100000) {
    struct tm* timeinfo = localtime(&now);
    Serial.println();
    Serial.printf("Thoi gian hien tai: %02d:%02d:%02d\n", 
                  timeinfo->tm_hour, timeinfo->tm_min, timeinfo->tm_sec);
  } else {
    Serial.println();
    Serial.println("Khong the dong bo thoi gian NTP!");
  }
  
  Serial.println("Firebase: Ready");
  
  // Khởi tạo seed cho hàm random (ESP8266 sử dụng A0)
  randomSeed(analogRead(A0));
}

void loop() {
  // Kiểm tra xem đã đến lúc gửi dữ liệu chưa
  if (millis() - lastSendTime >= sendInterval) {

    float randomValue = random(0.0, 107.0);
    
    // Gửi dữ liệu lên Firebase
    sendToFirebase(randomValue);
    
    lastSendTime = millis();
  }
}

void sendToFirebase(int value) {
  // Kiểm tra kết nối WiFi
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    WiFiClientSecure client;
    
    // Bỏ qua SSL certificate verification (chỉ dùng cho test)
    client.setInsecure();
    
    // Lấy thời gian hiện tại
    time_t now = time(nullptr);
    
    // Kiểm tra xem thời gian đã được đồng bộ chưa
    if (now < 100000) {
      Serial.println("❌ Thoi gian chua duoc dong bo, gui gia tri so don");
      String jsonString = "{\"data\":" + String(value) + "}";
      
      // Tạo URL Firebase với xác thực
      String url = String(firebaseUrl) + "data.json?auth=" + authToken;
      
      http.begin(client, url);
      http.addHeader("Content-Type", "application/json");
      http.addHeader("User-Agent", "ESP8266");
      
      Serial.println("=== SENDING DATA (NO TIME) ===");
      Serial.print("Value: ");
      Serial.println(value);
      Serial.print("JSON: ");
      Serial.println(jsonString);
      
      int httpResponseCode = http.PUT(jsonString);
      if (httpResponseCode > 0) {
        Serial.println("SUCCESS");
      } else {
        Serial.println("ERROR");
      }
      http.end();
      return;
    }
    
    // Thời gian đã được đồng bộ, tạo format đầy đủ
    struct tm* timeinfo = localtime(&now);
    
    // Tạo chuỗi giờ theo format HHhMM (ví dụ: 18h05)
    String currentTime = "";
    if (timeinfo->tm_hour < 10) currentTime += "0";
    currentTime += String(timeinfo->tm_hour) + "h";
    if (timeinfo->tm_min < 10) currentTime += "0";
    currentTime += String(timeinfo->tm_min);
    
    // Tạo string format "giờ:value" (ví dụ: "18h05:7")
    String timeValueString = currentTime + ":" + String(value);
    
    // Tạo JSON string với format {"data": "18h05:7"}
    String jsonString = "{\"data\":\"" + timeValueString + "\"}";
    
    // Tạo URL Firebase với xác thực
    String url = String(firebaseUrl) + "data.json?auth=" + authToken;
    
    http.begin(client, url);
    http.addHeader("Content-Type", "application/json");
    http.addHeader("User-Agent", "ESP8266");
    
    Serial.println("=== SENDING DATA ===");
    Serial.print("URL: ");
    Serial.println(url);
    Serial.print("Time: ");
    Serial.println(currentTime);
    Serial.print("Value: ");
    Serial.println(value);
    Serial.print("Data: ");
    Serial.println(timeValueString);
    Serial.print("JSON: ");
    Serial.println(jsonString);
    Serial.print("Status: ");
    
    // Gửi dữ liệu bằng phương thức PUT
    int httpResponseCode = http.PUT(jsonString);
    
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("SUCCESS");
      Serial.print("HTTP Code: ");
      Serial.println(httpResponseCode);
      Serial.print("Response: ");
      Serial.println(response);
    } else {
      Serial.println("ERROR");
      Serial.print("Error Code: ");
      Serial.println(httpResponseCode);
      Serial.print("Error: ");
      Serial.println(http.errorToString(httpResponseCode));
    }
    
    Serial.println("===================");
    http.end();
  } else {
    Serial.println("WiFi chua duoc ket noi!");
  }
} 