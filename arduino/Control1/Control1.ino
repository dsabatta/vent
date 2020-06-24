// Control constants
#define POT_MAX         630
#define POT_MIN         370
#define P_BSTART        180
#define MAX_SPEED       150
#define CTRL_P          10
#define CTRL_OFS        20

// Adjustable parameters
int P_MAX = 400;
int INHALE_TIME = 1000;
int EXHALE_TIME = 2000;
int RUNNING = 0;

int potVal;
int pressVal;
int speed;
long lastPrint = -100;
uint8_t state;

void allStop()
{
  speed = 0;
  analogWrite(5, 0);
  delay(10);
  digitalWrite(3, LOW);
  digitalWrite(4, LOW);
}

void setSpeed()
{
  // Limit check speed input
  speed = (speed > MAX_SPEED) ? MAX_SPEED : speed;
  speed = (speed < 0) ? 0 : speed;

  // Set desired speed
  analogWrite(5, speed);
}

void closeArms()
{
  // Close motor arms
  digitalWrite(4, HIGH);
}

void openArms()
{
  // Open motor arms
  digitalWrite(3, HIGH);
}

int readInt()
{
  if(Serial.available() < 3)
    return 0;

  int val = 0;
  val += Serial.read() - '0';
  val *= 10;
  val += Serial.read() - '0';
  val *= 10;
  val += Serial.read() - '0';

  return val;
}

void doSerialRead()
{
  // Check for minimum required characters
  if(Serial.available() < 4)
    return;

  switch(Serial.read())
  {
    case 'E':
      EXHALE_TIME = readInt() * 10;
      EXHALE_TIME = (EXHALE_TIME > 10000) ? 10000 : EXHALE_TIME;
      EXHALE_TIME = (EXHALE_TIME < 0) ? 0 : EXHALE_TIME;
      break;
    case 'I':
      INHALE_TIME = readInt() * 10;
      INHALE_TIME = (INHALE_TIME > 10000) ? 10000 : INHALE_TIME;
      INHALE_TIME = (INHALE_TIME < 0) ? 0 : INHALE_TIME;
      break;
    case 'P':
      P_MAX = readInt();
      P_MAX = (P_MAX > 10000) ? 10000 : P_MAX;
      P_MAX = (P_MAX < 0) ? 0 : P_MAX;
      break;
    case 'R':
      RUNNING = readInt();
      RUNNING = (RUNNING > 0) ? 1 : 0;
      break;
    default:
      break;
  }
}

int readInputs()
{
  // Read the analog values
  potVal = analogRead(A0);
  pressVal = analogRead(A1);

  // React to out of bounds pot values
  if ((potVal < 200) || (potVal > (POT_MAX+50)))
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

  // Send values to computer for plotting
  if((millis() - lastPrint) >= 20)
  {
    Serial.print(potVal);
    Serial.print(",");
    Serial.print(pressVal);
    Serial.print(",");
    Serial.println(state);
    lastPrint += 20;

    // Check if anything is available for reading
    doSerialRead();
  }
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

  // Initial operating state
  state = 0;

  // Start up serial port
  Serial.begin(115200);

  // Initial read of analog values
  readInputs();

  // Open arms to maximum extent
  speed = MAX_SPEED;
  setSpeed();
  openArms();
  while(digitalRead(8) == HIGH);
  allStop();
}

uint32_t breathStart;
uint32_t inhalationTime;
uint32_t exhalationTime;

void loop() {
  // Wait for operation to start
  while(RUNNING == 0) 
  {
    state = 0;
    readInputs();
  }
  
  // Calculate the breath intervals
  breathStart = millis();
  inhalationTime = breathStart + INHALE_TIME;
  exhalationTime = inhalationTime + EXHALE_TIME;

  state = 1;
  while(millis() < inhalationTime)
  {
    // Do inhale
    readInputs();
    if(potVal < POT_MAX) {
      speed = CTRL_P * (P_MAX - pressVal) + CTRL_OFS;
      setSpeed();
      closeArms();
    }
    else
    {
      allStop();
    }
  }
  
  state = 2;
  allStop();
  while(millis() < (inhalationTime + 100))
  {
    readInputs();
  }

  state = 3;
  while(millis() < exhalationTime)
  {
    // Do exhale
    readInputs();
    if(potVal > POT_MIN) {
      speed = MAX_SPEED;
      setSpeed();
      openArms();
    }
    else
    {
      allStop();
      break;
    }
  }

  state = 4;
  allStop();
  while(millis() < exhalationTime)
  {
    readInputs();
  }
}
