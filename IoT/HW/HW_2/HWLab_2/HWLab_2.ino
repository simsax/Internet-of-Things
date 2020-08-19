#include <LiquidCrystal_PCF8574.h>
#include <TimerOne.h>

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

float temp_min_fan = 23; // input format: fm0
float temp_max_fan = 28; // fM0
float temp_min_led = 10; // lm0
float temp_max_led = 15; // lM0
float temp_min_fanP = 25; // fm1
float temp_max_fanP = 30; // fM1
float temp_min_ledP = 15; // lm1
float temp_max_ledP = 20; // lM1

volatile int pres = 0;
volatile int timeout_pir = 1800; //secondi
volatile int timeout_sound = 3600;
volatile int seconds = 0;
volatile int sound_seconds = 0;
volatile int n_sound_events = 0;
volatile int sound_interval = 600; //10 minuti
volatile int lcd_seconds = 0;

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
  }
}

void lcd_print1() {
  lcd.clear();
  lcd.home();
  lcd.print("T:");
  lcd.print(temperature,1);
  lcd.print((String)" Pres:"+pres);
  lcd.setCursor(0,1);
  lcd.print((String)"AC:"+fanPerc+"% HT:"+heatPerc+"%");
}

void lcd_print2(float mf, float Mf, float ml, float Ml) {
  lcd.clear();
  lcd.home();
  lcd.print("AC m:");
  lcd.print(mf,1);
  lcd.print(" M:");
  lcd.print(Mf,1);
  lcd.setCursor(0,1);
  lcd.print("HT m:");
  lcd.print(ml,1);
  lcd.print(" M:");
  lcd.print(Ml,1);
}

void checkInput() { 
  if (Serial.available() > 0) {
     String input = Serial.readString();
     String command = input.substring(0,3);
     float temp = input.substring(4).toFloat();
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
}

void loop() {
  temperature = readTemperature();
  if (lcd_seconds>=0 && lcd_seconds<5)
    lcd_print1();
  if (pres==1) {
    airConditioner(temperature, temp_min_fanP, temp_max_fanP);
    heater(temperature, temp_min_ledP, temp_max_ledP);
    if (lcd_seconds>=5 && lcd_seconds<10)
      lcd_print2(temp_min_fanP, temp_max_fanP, temp_min_ledP, temp_max_ledP);
  }
  else if (pres==0) {
    airConditioner(temperature, temp_min_fan, temp_max_fan);
    heater(temperature, temp_min_led, temp_max_led);
    if (lcd_seconds>=5 && lcd_seconds<10)
      lcd_print2(temp_min_fan, temp_max_fan, temp_min_led, temp_max_led);
  }
  checkSound();
  checkInput();
}
