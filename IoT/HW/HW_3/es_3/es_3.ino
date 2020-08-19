#include <MQTTclient.h>
#include <Process.h>
#include <Bridge.h>
#include <ArduinoJson.h>

const size_t capacity = JSON_ARRAY_SIZE(1) + JSON_OBJECT_SIZE(2) + JSON_OBJECT_SIZE(4) + 40;
DynamicJsonDocument doc_rec(capacity);
DynamicJsonDocument doc_snd(capacity);

const int LED_PIN = 12;
const int TEMP_PIN = A1;
const int B = 4275;
const long int R0 = 100000;
String my_base_topic = "/tiot/8";

String senMlEncode(float v) {
  doc_snd.clear();
  doc_snd["bn"] = "Yun";
  doc_snd["e"][0]["n"] = "temperature";
  doc_snd["e"][0]["t"] = millis()/1000; //secondi
  doc_snd["e"][0]["v"] = ((int)(v*100))/100.0;
  doc_snd["e"][0]["u"] = "Cel";

  String output;
  serializeJson(doc_snd, output);
  return output;
}

float calcTemp() {
  int Vsig = analogRead(TEMP_PIN);
  float R = (1023.0/Vsig-1.0)*R0;
  float temp = 1.0/(log(R/R0)/B+1/298.15)-273.15;
  return temp;
}

void setLedValue(const String& topic, const String& subtopic, const String& message) {
  DeserializationError err = deserializeJson(doc_rec, message);
  if (err) {
    Serial.print(F("deserializeJson() failed with code "));
    Serial.println(err.c_str());
  }
  if (doc_rec["bn"]=="Yun" && doc_rec["e"][0]["n"]=="led" && doc_rec["e"][0]["u"]==(char*)NULL) {
    if (doc_rec["e"][0]["v"]==1)
      digitalWrite(LED_PIN, HIGH);
    else if (doc_rec["e"][0]["v"]==0)
      digitalWrite(LED_PIN, LOW);
    else
      Serial.println("Error: value format is incorrect.");
  }
  else
    Serial.println("Error: message format is incorrect.");
}

void setup() {
  Serial.begin(9600); 
  while (!Serial);
  Serial.println("Running...");
  pinMode(LED_PIN, OUTPUT);
  pinMode(TEMP_PIN, INPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  digitalWrite(LED_BUILTIN, LOW);
  Bridge.begin();
  digitalWrite(LED_BUILTIN, HIGH);
  mqtt.begin("test.mosquitto.org",1883);
  mqtt.subscribe(my_base_topic + String("/led"), setLedValue);
}

void loop() {  
  mqtt.monitor();
  
  String  message = senMlEncode(calcTemp());
  mqtt.publish(my_base_topic + String("/temperature"), message);

  delay(1e03);
}
