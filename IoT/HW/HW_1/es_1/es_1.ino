#include <TimerOne.h>

const int RLED_PIN = 12;
const int GLED_PIN = 11;

const float R_HALF_PERIOD = 1.5;
const float G_HALF_PERIOD = 3.5;

int gLedState = LOW; //0 logico
int rLedState = LOW;

void blinkGreen() {
  gLedState = !gLedState;
  digitalWrite(GLED_PIN, gLedState);
}


void setup() {
  pinMode(RLED_PIN, OUTPUT);
  pinMode(GLED_PIN, OUTPUT);
  Timer1.initialize(G_HALF_PERIOD*1e06);
  Timer1.attachInterrupt(blinkGreen);
}

void loop() {
  rLedState = !rLedState;
  digitalWrite(RLED_PIN, rLedState);
  delay(R_HALF_PERIOD*1e03);
}
