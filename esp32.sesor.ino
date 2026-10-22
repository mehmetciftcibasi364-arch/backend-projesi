#include <WiFi.h>
#include <HTTPClient.h>

const char* ssid = "WIFI_ADI";
const char* password = "WIFI_SIFRESI";

const char* serverUrl = "BACKEND_API_ADRESI/api/sensors";
void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;

    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");

    String jsonData = R"({
      "device_id": "ESP32-001",
      "temperature": 26.8,
      "humidity": 61.5,
      "soil_moisture": 38.2
    })";

    int httpResponseCode = http.POST(jsonData);

    Serial.print("HTTP response: ");
    Serial.println(httpResponseCode);

    http.end();
  }

  delay(60000);
}
