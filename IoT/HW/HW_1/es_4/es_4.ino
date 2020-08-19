#define STEP 10
float current_speed = 0;
const int FAN_PIN = 6;

void setup() {
  Serial.begin(9600);
  while(!Serial);
  Serial.println("Lab 1.4 starting");
  pinMode(FAN_PIN, OUTPUT);
  analogWrite(FAN_PIN, (int) current_speed);
}

void checkInput() {
  int speedPerc=0;
  if (Serial.available() > 0) {
    int inByte = Serial.read();
    if (inByte == '+') {
      if (current_speed < 255) {
        current_speed += (float)255/STEP; 
        speedPerc = current_speed/255*100;
        Serial.println((String)"Increasing speed: " + speedPerc + "%");
        analogWrite(FAN_PIN, (int) current_speed);
      }
      else
        Serial.println("Already at max speed");
    } 
    else if (inByte == '-') {
      if (current_speed > 0) {
        current_speed -= (float)255/STEP;
        speedPerc = current_speed/255*100;
        Serial.println((String)"Decreasing speed: " + speedPerc + "%");
        analogWrite(FAN_PIN, (int) current_speed);
      }
      else
        Serial.println("Already at min speed");
   }
   else
    Serial.println("Invalid command");
  }
}

void loop() {
  checkInput();
}
