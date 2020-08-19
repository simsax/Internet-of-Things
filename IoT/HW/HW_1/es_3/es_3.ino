const int GLED_PIN = 11;
const int PIR_PIN = 7;

volatile int tot_count = 0;

void checkPresence() {
  volatile int pir_state = digitalRead(PIR_PIN);
  digitalWrite(GLED_PIN, pir_state);
  if (pir_state == HIGH)
    tot_count++;
}

void setup() {
  Serial.begin(9600); //velocità connessione
  while (!Serial); //programma non parte finchè non apro serial monitor
  Serial.println("Lab 1.3 Starting");
  pinMode(GLED_PIN, OUTPUT);
  pinMode(PIR_PIN, INPUT);
  attachInterrupt(digitalPinToInterrupt(PIR_PIN), checkPresence, CHANGE);
}

void loop() {
  Serial.print("Total people count: ");
  Serial.println(tot_count);
  delay(10*1e03);
}
