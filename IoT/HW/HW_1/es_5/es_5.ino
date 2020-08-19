const int TEMP_PIN = A1;
const int B = 4275;
const long int R0 = 100000;

void setup() {
  Serial.begin(9600); //velocità connessione
  while (!Serial); //programma non parte finchè non apro serial monitor
  Serial.println("Lab 1.5 Starting");
  pinMode(TEMP_PIN, INPUT);
}

void loop() {
  int Vsig = analogRead(TEMP_PIN);
  float R = (1023.0/Vsig-1.0)*R0;
  float temperature = 1.0/(log(R/R0)/B+1/298.15)-273.15;
  Serial.println((String)"Temperature: " + temperature + "°C");
  delay(10*1e03);
}
