void allStop()
{
  analogWrite(5, 0);
  delay(10);
  digitalWrite(3, LOW);
  digitalWrite(4, LOW);
}

void setup() {
  // Position input
  pinMode(A0, INPUT);
  pinMode(A1, INPUT);
  // Homing switch
  pinMode(8, OUTPUT);
  digitalWrite(8, HIGH);
  // Status LED
  pinMode(13, OUTPUT);

  // Motor PWM
  pinMode(5, OUTPUT);
  digitalWrite(5, LOW);

  // Motor direction control pins
  pinMode(3, OUTPUT);
  pinMode(4, OUTPUT);
  digitalWrite(3, LOW);
  digitalWrite(4, LOW);
  allStop();

  // Start up serial port
  Serial.begin(115200);
}

uint16_t v1, v2;

void loop() {
  v1 = analogRead(A0);
  v2 = analogRead(A1);
  
  Serial.print(v1);
  Serial.print(',');
  Serial.println(v2);
  delay(20);
}
