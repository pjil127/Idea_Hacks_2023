/*
 * This ESP32 code is created by esp32io.com
 *
 * This ESP32 code is released in the public domain
 *
 * For more detail (instruction and wiring diagram), visit https://esp32io.com/tutorials/esp32-servo-motor
 */

#include <ESP32Servo.h>
#include <ArduinoMqttClient.h>

#if defined(ARDUINO_SAMD_MKRWIFI1010) || defined(ARDUINO_SAMD_NANO_33_IOT) || defined(ARDUINO_AVR_UNO_WIFI_REV2)
  #include <WiFiNINA.h>
#elif defined(ARDUINO_SAMD_MKR1000)
  #include <WiFi101.h>
#elif defined(ARDUINO_ARCH_ESP8266)
  #include <ESP8266WiFi.h>
#elif defined(ARDUINO_ARCH_ESP32)
  #include <WiFi.h>
#endif

#define SERVO_PIN 13 // ESP32 pin GIOP26 connected to servo motor
#define SERVO_PIN2 12 // ESP32 pin GIOP26 connected to servo motor
#define SERVO_PIN3 26 // ESP32 pin GIOP26 connected to servo motor
#define SERVO_PIN4 27 // ESP32 pin GIOP26 connected to servo motor

char ssid[] = "Lemon";    // your network SSID (name)
char pass[] = "jillianl";    // your network password (use for WPA, or use as key for WEP)

WiFiClient wifiClient;
MqttClient mqttClient(wifiClient);

const char broker[] = "test.mosquitto.org";
int        port     = 1883;
const char topic[]  = "arduino/simple/lemur";

Servo servoMotor, servoMotor2, servoMotor3, servoMotor4;

int roshambo = 0;
void setup() {
  //Initialize serial and wait for port to open:
  Serial.begin(115200);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }

  // attempt to connect to WiFi network:
  Serial.print("Attempting to connect to WPA SSID: ");
  Serial.println(ssid);
  WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED) {
    // failed, retry
    WiFi.begin(ssid, pass);
    Serial.print(".");
    delay(5000);
  }

  Serial.println("You're connected to the network");
  Serial.println();

  Serial.print("Attempting to connect to the MQTT broker: ");
  Serial.println(broker);

  if (!mqttClient.connect(broker, port)) {
    Serial.print("MQTT connection failed! Error code = ");
    Serial.println(mqttClient.connectError());

    while (1);
  }

  Serial.println("You're connected to the MQTT broker!");
  Serial.println();

  Serial.print("Subscribing to topic: ");
  Serial.println(topic);
  Serial.println();

  // subscribe to a topic
  mqttClient.subscribe(topic);

  // topics can be unsubscribed using:
  // mqttClient.unsubscribe(topic);

  Serial.print("Waiting for messages on topic: ");
  Serial.println(topic);
  Serial.println();

  servoMotor.attach(SERVO_PIN);  // attaches the servo on ESP32 pin
  servoMotor2.attach(SERVO_PIN2);  // attaches the servo on ESP32 pin
  servoMotor3.attach(SERVO_PIN3);  // attaches the servo on ESP32 pin
  servoMotor4.attach(SERVO_PIN4);  // attaches the servo on ESP32 pin

  servoMotor2.write(100);
  servoMotor.write(170);
}

void do_scissors()
{
  for (int pos = 170; pos >= 20; pos -= 1) {
    servoMotor.write(pos);
    delay(15); // waits 15ms to reach the position
  }
}

void undo_scissors()
{
  for (int pos = 20; pos <= 170; pos += 1) {
    servoMotor.write(pos);
    delay(15); // waits 15ms to reach the position
  }
}
void do_paper()
{
    for (int pos2 = 100, pos = 170; pos2 >= 10 && pos >= 20; pos2 -= 1, pos -= 2) {
    servoMotor2.write(pos2);
    delay(15); // waits 15ms to reach the position
    servoMotor.write(pos);
    delay(30); // waits 15ms to reach the position
  }
  
}

void undo_paper()
{
    for (int pos2 = 10, pos = 20; pos2 <= 100 && pos <= 170; pos2 += 1, pos += 2) {
    servoMotor2.write(pos2);
    delay(15); // waits 15ms to reach the position
    servoMotor.write(pos);
    delay(30); // waits 15ms to reach the position
  }
  
}


void loop() {

  int messageSize = mqttClient.parseMessage();
  if (messageSize) {
//    // we received a message, print out the topic and contents
//    Serial.print("Received a message with topic '");
//    Serial.print(mqttClient.messageTopic());
//    Serial.print("', length ");
//    Serial.print(messageSize);
//    Serial.println(" bytes:");

    // use the Stream interface to print the contents
    while (mqttClient.available()) {
      char s = (char)mqttClient.read();
      Serial.println(s);
      if (s == '3'){
        servoMotor.write(20);
        delay(2000);
        servoMotor2.write(100);
        servoMotor.write(170);
       }
       else if (s == '2') {
        servoMotor2.write(10);
        servoMotor.write(20);
        delay(2000);
        servoMotor2.write(100);
        servoMotor.write(170);
      }
       else if (s == '1'){
        servoMotor2.write(100);
        servoMotor.write(170);
      }
      
  }
//
//  if (roshambo == 1)
//    Serial.println("1!");
//  else if (roshambo == 2)
//    Serial.println("2!");
//  else if (roshambo == 3)
//    Serial.println("3!");
  }  
}