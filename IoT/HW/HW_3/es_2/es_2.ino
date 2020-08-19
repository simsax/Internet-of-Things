#include <Bridge.h>
#include <ArduinoJson.h>
#include <Process.h>

const size_t capacity1 = JSON_ARRAY_SIZE(1) + JSON_OBJECT_SIZE(2) + JSON_OBJECT_SIZE(4) + 40;
DynamicJsonDocument doc1(capacity1);
const size_t capacity2 = JSON_OBJECT_SIZE(4) + 120;
DynamicJsonDocument doc2(capacity2);

String url1 = "http://192.168.1.4:8080/log";
String url2 = "http://192.168.1.4:8080/devices";

const int TEMP_PIN = A1;
const int B = 4275;
const long int R0 = 100000;

String senMlEncode1(float v) {
  doc1.clear();
  doc1["bn"] = "Yun";
  doc1["e"][0]["n"] = "temperature";
  doc1["e"][0]["t"] = millis()/1000; //secondi
  doc1["e"][0]["v"] = ((int)(v*100))/100.0;
  doc1["e"][0]["u"] = "Cel";

  String output;
  serializeJson(doc1, output);
  return output;
}

String senMlEncode2() {
  doc2.clear();
  doc2["deviceID"] = "Yun_temperature";
  doc2["RESTuri"] = "/yun/temperature";
  doc2["MQTTtopic"] = "/tiot/8/temperature";
  doc2["resource"] = "Temperature sensor";

  String output;
  serializeJson(doc2, output);
  return output;
}

int postRequest1(String body) {
  Process p;
  p.begin("curl");
  p.addParameter("-H");
  p.addParameter("Content-Type: application/json");
  p.addParameter("-X");
  p.addParameter("POST");
  p.addParameter("-d");
  p.addParameter(body);
  p.addParameter(url1);
  p.run();

  return p.exitValue(); 
}

int postRequest2(String body) {
  Process p;
  p.begin("curl");
  p.addParameter("-H");
  p.addParameter("Content-Type: application/json");
  p.addParameter("-X");
  p.addParameter("POST");
  p.addParameter("-d");
  p.addParameter(body);
  p.addParameter(url2);
  p.run();

  return p.exitValue(); 
}

float calcTemp() {
  int Vsig = analogRead(TEMP_PIN);
  float R = (1023.0/Vsig-1.0)*R0;
  float temp = 1.0/(log(R/R0)/B+1/298.15)-273.15;
  return temp;
}

void setup() {
  Serial.begin(9600); 
  while (!Serial);
  pinMode(TEMP_PIN, INPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
  Bridge.begin();
  digitalWrite(LED_BUILTIN, HIGH);
}

void loop() {
  //int res = postRequest1(senMlEncode1(calcTemp()));
  int res = postRequest2(senMlEncode2());
  if (res==0)
    Serial.println("POST request success");
  else
    Serial.println((String)"Error. Return code: " + res);
  delay(60*1e3); 
}
