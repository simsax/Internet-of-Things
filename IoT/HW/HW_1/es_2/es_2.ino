#include <TimerOne.h>

const int RLED_PIN = 12;
const int GLED_PIN = 11;

const float R_HALF_PERIOD = 1.5;
const float G_HALF_PERIOD = 3.5;

volatile int gLedState = LOW; //0 logico
volatile int rLedState = LOW;

void blinkGreen() {
  gLedState = !gLedState;
  digitalWrite(GLED_PIN, gLedState);
}

void serialPrintStatus() {
  if (Serial.available() > 0) { //guarda se ci sono byte disponibili sul Serial buffer
    int inByte = Serial.read(); //legge un byte dal buffer
    if (inByte == 'R' || inByte == 'r') {
      if (rLedState == LOW)
        Serial.println("LED R Status: 0");
      else
        Serial.println("LED R Status: 1");
    }
    else if (inByte == 'G' || inByte == 'g') {
      if (gLedState == LOW)
        Serial.println("LED G Status: 0");
      else
        Serial.println("LED G Status: 1");
    }
    else
      Serial.println("Invalid command");
  }  
}

void setup() {
  Serial.begin(9600); //velocità connessione
  while (!Serial); //programma non parte finchè non apro serial monitor
  Serial.println("Lab 1.2 Starting");
  pinMode(RLED_PIN, OUTPUT);
  pinMode(GLED_PIN, OUTPUT);
  Timer1.initialize(10*1e06);
  Timer1.attachInterrupt(blinkGreen);
}

void loop() {
  serialPrintStatus();
  rLedState = !rLedState;
  digitalWrite(RLED_PIN, rLedState);
  delay(R_HALF_PERIOD*1e03);
}
