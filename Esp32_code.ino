#include <WiFi.h>

#define IN1 5
#define IN2 18
#define IN3 19
#define IN4 21

// Wi-Fi credentials
const char* ssid = "vivo V301";
const char* password = "nopassword";

// TCP server on port 1234
WiFiServer server(1234);

void setup() {
  Serial.begin(115200);

  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  stopMotors();

  WiFi.begin(ssid, password);
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  server.begin();
  Serial.println("TCP Server started");
}

void loop() {
  WiFiClient client = server.available();
  if (client) {
    Serial.println("Client connected");

    while (client.connected()) {
      if (client.available()) {
        char cmd = client.read();
        Serial.print("Received: ");
        Serial.println(cmd);

        // Stop motors before new command
        stopMotors();
        delay(50);  // small delay for safety

        switch (cmd) {
          case 'F': forward(); break;
          case 'B': backward(); break;
          case 'L': left(); break;
          case 'R': right(); break;
          case 'S': stopMotors(); break;
        }
      }
    }

    client.stop();
    Serial.println("Client disconnected");
  }
}

void forward() {
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
}

void backward() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
}

void left() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
}

void right() {
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
}

void stopMotors() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
}

