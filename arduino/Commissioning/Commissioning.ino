#define POT_MAX   630
#define POT_MIN   350

void allStop()
{
  analogWrite(5, 0);
  delay(10);
  digitalWrite(3, LOW);
  digitalWrite(4, LOW);
}

void closeArms(uint8_t speed)
{
  analogWrite(5, speed);
  digitalWrite(4, HIGH);
}

void openArms(uint8_t speed)
{
  analogWrite(5, speed);
  digitalWrite(3, HIGH);
}

int readPot()
{
  int val = analogRead(A0);
  if ((val < 50) || (val > 800))
  {
    allStop();
    while(1)
    {
      digitalWrite(13, HIGH);
      delay(150);
      digitalWrite(13, LOW);
      delay(150);
    }
  }

  return val;
}

void setup() {
  // Position input
  //pinMode(A0, INPUT);
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

  // Start up serial port
  Serial.begin(115200);

  // Open arms to maximum extent
  openArms(150);
  while(digitalRead(8) == HIGH);
  allStop();
}

void loop() {
//  Serial.println(analogRead(A0));
//  delay(200);
  
  closeArms(150);
  while(readPot() < POT_MAX);
  allStop();
  delay(250);
  openArms(150);
  while(readPot() > POT_MIN);
  allStop();
  delay(750);
}
