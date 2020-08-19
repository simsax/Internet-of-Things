#include <LiquidCrystal_PCF8574.h>

LiquidCrystal_PCF8574 lcd(0x27);

const int TEMP_PIN = A1;
const int B = 4275;
const long int R0 = 100000;

void setup() {
  lcd.begin(16,2);
  lcd.setBacklight(255);
  lcd.home();
  lcd.clear();
  lcd.print("Temperature:");
  pinMode(TEMP_PIN, INPUT);
}

void loop() {
  int Vsig = analogRead(TEMP_PIN);
  float R = (1023.0/Vsig-1.0)*R0;
  float temperature = 1.0/(log(R/R0)/B+1/298.15)-273.15;
  lcd.setCursor(12,0);
  lcd.print(temperature);
  delay(10*1e03);
}
