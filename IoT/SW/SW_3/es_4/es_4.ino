#include <LiquidCrystal_PCF8574.h>
#include <TimerOne.h>
#include <MQTTclient.h>
#include <Process.h>
#include <Bridge.h>
#include <ArduinoJson.h>

const size_t capacity = JSON_ARRAY_SIZE(1) + JSON_OBJECT_SIZE(2) + JSON_OBJECT_SIZE(4) + 50;
DynamicJsonDocument doc_snd(capacity);
DynamicJsonDocument doc_rec(capacity);

const size_t capacity2 = JSON_OBJECT_SIZE(4) + 120;
DynamicJsonDocument doc2(capacity2);

LiquidCrystal_PCF8574 lcd(0x27);
const int RLED_PIN = 11;
const int GLED_PIN = 12;
const int PIR_PIN = 7;
const int FAN_PIN = 6;
const int TEMP_PIN = A1;
const int SOUND_PIN = 5;
const int B = 4275;
const long int R0 = 100000;
int fanPerc = 0;
int heatPerc = 0;
float temperature = 0;
String my_base_topic = "/tiot/8";

float temp_min_fan = 23; // input format: fm0
float temp_max_fan = 28; // fM0
float temp_min_led = 10; // lm0
float temp_max_led = 15; // lM0
float temp_min_fanP = 25; // fm1
float temp_max_fanP = 30; // fM1
float temp_min_ledP = 15; // lm1
float temp_max_ledP = 20; // lM1

volatile int pres = 0;
volatile int noise = 0;
volatile int timeout_pir = 1800; //secondi
volatile int timeout_sound = 3600;
volatile int seconds = 0;
volatile int sound_seconds = 0;
volatile int n_sound_events = 0;
volatile int sound_interval = 600; //10 minuti
volatile int lcd_seconds = 0;

String senMlEncodeRegT() {
  doc2.clear();
  doc2["deviceID"] = "Yun_temperature";
  doc2["RESTuri"] = "/yun/temperature";
  doc2["MQTTtopic"] = "/tiot/8/temperature";
  doc2["resource"] = "Temperature sensor";

  String output;
  serializeJson(doc2, output);
  return output;
}

String senMlEncodeRegPres() {
  doc2.clear();
  doc2["deviceID"] = "Yun_presence";
  doc2["RESTuri"] = "/yun/presence";
  doc2["MQTTtopic"] = "/tiot/8/presence";
  doc2["resource"] = "Presence";

  String output;
  serializeJson(doc2, output);
  return output;
}

String senMlEncodeRegN() {
  doc2.clear();
  doc2["deviceID"] = "Yun_noise";
  doc2["RESTuri"] = "/yun/noise";
  doc2["MQTTtopic"] = "/tiot/8/noise";
  doc2["resource"] = "Noise sensor";

  String output;
  serializeJson(doc2, output);
  return output;
}

String senMlEncodeRegSetPoint() {
  doc2.clear();
  doc2["deviceID"] = "Yun_setpoints";
  doc2["RESTuri"] = "/yun/setpoints";
  doc2["MQTTtopic"] = "/tiot/8/setpoints";
  doc2["resource"] = "Temperature set points";

  String output;
  serializeJson(doc2, output);
  return output;
}

String senMlEncodeRegLCD() {
  doc2.clear();
  doc2["deviceID"] = "Yun_lcd";
  doc2["RESTuri"] = "/yun/lcd";
  doc2["MQTTtopic"] = "/tiot/8/lcd";
  doc2["resource"] = "LCD monitor";

  String output;
  serializeJson(doc2, output);
  return output;
}

String senMlEncodeT(float v) {
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

String senMlEncodeP() {
  doc_snd.clear();
  doc_snd["bn"] = "Yun";
  doc_snd["e"][0]["n"] = "presence";
  doc_snd["e"][0]["t"] = millis()/1000; //secondi
  doc_snd["e"][0]["v"] = pres;
  doc_snd["e"][0]["u"] = (char*)NULL;

  String output;
  serializeJson(doc_snd, output);
  return output;
}

String senMlEncodeN() {
  doc_snd.clear();
  doc_snd["bn"] = "Yun";
  doc_snd["e"][0]["n"] = "noise";
  doc_snd["e"][0]["t"] = millis()/1000; //secondi
  doc_snd["e"][0]["v"] = noise;
  doc_snd["e"][0]["u"] = (char*)NULL;

  String output;
  serializeJson(doc_snd, output);
  return output;
}

float readTemperature() {
  int Vsig = analogRead(TEMP_PIN);
  float R = (1023.0/Vsig-1.0)*R0;
  return 1.0/(log(R/R0)/B+1/298.15)-273.15;
}

void airConditioner(float temperature, float tmin, float tmax) {
  float speed=0;
  if (temperature>=tmin && temperature<=tmax) {
    speed = (float)255*(temperature-tmin)/(tmax-tmin);
    analogWrite(FAN_PIN, (int)speed);
  }
  else if (temperature<tmin) {
    speed = 0;
    analogWrite(FAN_PIN, (int)speed);
  }
   else if (temperature>tmax) {
    speed = 255;
    analogWrite(FAN_PIN, (int)speed);
  }
  fanPerc = speed/255*100;
}

void heater(float temperature, float tmin, float tmax) {
  float heat = 0;
  if (temperature>=tmin && temperature<=tmax) {
    heat = (float)(-255)*(temperature-tmin)/(tmax-tmin)+255;
    analogWrite(RLED_PIN, (int)heat);
  }
  else if (temperature<tmin) {
    heat = 255;
    analogWrite(RLED_PIN, (int)heat);
  }
  else if (temperature>tmax) {
    heat = 0;
    analogWrite(RLED_PIN, (int)heat);
  }
  heatPerc = heat/255*100;
}

void checkPir() {
  pres = 1;
  seconds = 0;
}

void resetPres() {
  seconds++;
  sound_seconds++;
  lcd_seconds++;
  if (lcd_seconds>10)
    lcd_seconds=0;
  if (sound_seconds==sound_interval) {
    if (n_sound_events>=50)
      pres = 1;
    sound_seconds = 0;
    n_sound_events=0;
  }
  else if (seconds>=timeout_pir && seconds>=timeout_sound && n_sound_events==0)
    pres = 0;
}

void checkSound() {
  if (digitalRead(SOUND_PIN)==LOW) {
    n_sound_events++;
    seconds = 0;
    delay(1000);

    noise=1;
  }
  else noise=0;
}

void checkInput(String command, float temp) { 
    if (command.equals("fm0"))
     temp_min_fan = temp;
    else if (command.equals("fM0"))
     temp_max_fan = temp;
    else if (command.equals("lm0"))
     temp_min_led = temp;
    else if (command.equals("lM0"))
     temp_max_led = temp;
    else if (command.equals("fm1"))
     temp_min_fanP = temp;
    else if (command.equals("fM1"))
     temp_max_fanP = temp;
    else if (command.equals("lm1"))
     temp_min_ledP = temp;
    else if (command.equals("lM1"))
     temp_max_ledP = temp;
    else
     Serial.println("Invalid command.");
}

void modifySetPoints(const String& topic, const String& subtopic, const String& message) {
  DeserializationError err = deserializeJson(doc_rec, message);
  if (err) {
    Serial.print(F("deserializeJson() failed with code "));
    Serial.println(err.c_str());
  }
  if (doc_rec["bn"]=="Yun_setpoints") {
    checkInput(doc_rec["e"][0]["n"],doc_rec["e"][0]["v"]); //assumo che come valore di "n" ci sia la stringa corrispondente al setpoint da cambiare e in "v" il suo valore
  }
  else
    Serial.println("Error: message format is incorrect.");
}

void displayMessage(const String& topic, const String& subtopic, const String& message) {
  DeserializationError err = deserializeJson(doc_rec, message);
  if (err) {
    Serial.print(F("deserializeJson() failed with code "));
    Serial.println(err.c_str());
  }
  if (doc_rec["bn"]=="Yun_lcd") {
    String message = doc_rec["e"][0]["v"];
    lcd.clear();
    lcd.home();
    lcd.print(message);
    if (message.length()>16)
      for (int i=0;i<message.length()-16;i++) {
        delay(1000);
        lcd.scrollDisplayLeft();
      }
  }
  else
    Serial.println("Error: message format is incorrect.");
}

void setup() {
  Serial.begin(9600);
  while(!Serial);
  Serial.println("HWLab2 starting");
  lcd.begin(16,2);
  lcd.setBacklight(255);
  lcd.home();
  lcd.clear();
  pinMode(FAN_PIN, OUTPUT);
  pinMode(TEMP_PIN, INPUT);
  pinMode(RLED_PIN, OUTPUT);
  pinMode(GLED_PIN, OUTPUT);
  pinMode(PIR_PIN, INPUT);
  pinMode(SOUND_PIN, INPUT);
  analogWrite(FAN_PIN, 0);
  analogWrite(RLED_PIN, 0);
  attachInterrupt(digitalPinToInterrupt(PIR_PIN), checkPir, RISING);
  Timer1.initialize(1e06);
  Timer1.attachInterrupt(resetPres);
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
  Bridge.begin();
  digitalWrite(LED_BUILTIN, HIGH);
  mqtt.begin("test.mosquitto.org",1883);
  mqtt.subscribe(my_base_topic + String("/setpoints"), modifySetPoints);
  mqtt.subscribe(my_base_topic + String("/lcd"), displayMessage);
}

void loop() {
  mqtt.monitor();
  
  temperature = readTemperature();
  if (pres==1) {
    airConditioner(temperature, temp_min_fanP, temp_max_fanP);
    heater(temperature, temp_min_ledP, temp_max_ledP);
  }
  else if (pres==0) {
    airConditioner(temperature, temp_min_fan, temp_max_fan);
    heater(temperature, temp_min_led, temp_max_led);
  }
  checkSound();

  //registra sensore temperatura nel catalog
  String message = senMlEncodeRegT();
  mqtt.publish(my_base_topic + String("/devices"), message);
  //pubblica valori di temperatura
  message = senMlEncodeT(readTemperature());
  mqtt.publish(my_base_topic + String("/temperature"), message);
 
  //registra presenze nel catalog
  message = senMlEncodeRegT();
  mqtt.publish(my_base_topic + String("/devices"), message);
  //pubblica valore della variabile pres
  message = senMlEncodeP();
  mqtt.publish(my_base_topic + String("/presence"), message);

  //registra sensore di rumore nel catalog
  message = senMlEncodeRegN();
  mqtt.publish(my_base_topic + String("/devices"), message);
  //pubblica valore della variabile noise
  message = senMlEncodeN();
  mqtt.publish(my_base_topic + String("/noise"), message);

  //registra set points nel catalog
  message = senMlEncodeRegSetPoint();
  mqtt.publish(my_base_topic + String("/devices"), message);

  //registra monitor lcd nel catalog
  message = senMlEncodeRegLCD();
  mqtt.publish(my_base_topic + String("/devices"), message);
}
