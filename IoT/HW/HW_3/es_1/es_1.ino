#include <Bridge.h>
#include <BridgeServer.h>
#include <BridgeClient.h>
#include <ArduinoJson.h>

const size_t capacity = JSON_ARRAY_SIZE(1) + JSON_OBJECT_SIZE(2) + JSON_OBJECT_SIZE(4) + 40;
DynamicJsonDocument doc(capacity);

BridgeServer server;
const int LED_PIN = 12;
const int TEMP_PIN = A1;
const int B = 4275;
const long int R0 = 100000;

String senMlEncode(String res, float v, String unit) {
  doc.clear();
  doc["bn"] = "Yun";
  doc["e"][0]["n"] = res;
  doc["e"][0]["t"] = millis()/1000; //secondi
  doc["e"][0]["v"] = ((int)(v*100))/100.0;
  if (unit!="") doc["e"][0]["u"] = unit;
  else doc["e"][0]["u"] = (char*)NULL;

  String output;
  serializeJson(doc, output);
  return output;
}

void printResponse(BridgeClient client, int code, String body) {
  client.println("Status: " + String(code));
  if (code == 200) {
    client.println(F("Content-type: application/json; charset=utf-8"));
    client.println(); //riga bianca obbligatoria
    client.println(body);
  }
}

void process(BridgeClient client) {
  String command = client.readStringUntil('/');
  command.trim(); //delete \n or similar

  if (command == "led") {
    int val = client.parseInt();
    if (val==0 || val==1) {
      digitalWrite(LED_PIN, val);
      printResponse(client, 200, senMlEncode(F("led"),val,F("")));
    } else {
      printResponse(client, 400, "");
    }
  }
  else if (command == "temperature") {
    int Vsig = analogRead(TEMP_PIN);
    float R = (1023.0/Vsig-1.0)*R0;
    float temp = 1.0/(log(R/R0)/B+1/298.15)-273.15;
    printResponse(client, 200, senMlEncode(F("temperature"),temp,F("Cel")));
  }
  else
    printResponse(client, 404, "");
}

void setup() {
  pinMode(LED_PIN, OUTPUT);
  pinMode(TEMP_PIN, INPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
  Bridge.begin();
  digitalWrite(LED_BUILTIN, HIGH);
  server.listenOnLocalhost();
  server.begin();
}

void loop() {
  BridgeClient client = server.accept();

  if (client) {
    process(client);
    client.stop();
  }
  delay(50);
}
