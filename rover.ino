// "SA" - attach servo
// "SD" - detach servo
// "S-45;" - "S45;" - move servo
// "D;" - get distance 

#define SENSOR_TRIGGER 11
#define SENSOR_ECHO 10
#define LED 13
#define SENSOR_SERVO 5

#define SENSOR_SERVO_FIX 20

#include <Servo.h>

Servo sensor_servo;
char buffer[10];

void setup() {
  Serial.begin(9600);
  pinMode(LED,OUTPUT);  
  pinMode(SENSOR_TRIGGER,OUTPUT);      
  pinMode(SENSOR_ECHO,INPUT);  
  sensor_servo.attach(SENSOR_SERVO);
  sensor_servo.write(90 + SENSOR_SERVO_FIX);  
}

void loop() {
  
  if (Serial.available() > 0) {
    int count = Serial.readBytesUntil(';', buffer, 10);
    if ((buffer[0] == 'd') || (buffer[0] == 'D'))
    {
      long d = getDistance();
      Serial.println(d);
    } 
    else if (buffer[0] == 'S' || buffer[0] == 's')
    {
      if (buffer[1] == 'A' || buffer[1] == 'a')
      {
        sensor_servo.attach(SENSOR_SERVO);
      }
      else if (buffer[1] == 'D' || buffer[1] == 'd')
      {
        sensor_servo.detach();
      }
      else
      {
        buffer[count] = 0;
        int alfa = atoi(buffer+1);
        if ((alfa >= -50) && (alfa <= 50))
        {
          sensor_servo.write(90 - alfa + SENSOR_SERVO_FIX);
        }
        delay(300);
      }
    }
  }
 
  delay(10);
}

long getDistance()
{
    digitalWrite(SENSOR_TRIGGER, LOW);
    delayMicroseconds(2);
    digitalWrite(SENSOR_TRIGGER, HIGH); 
    delayMicroseconds(10);
    digitalWrite(SENSOR_TRIGGER, LOW);
    long microseconds = pulseIn(SENSOR_ECHO, HIGH);  
    long cm = microseconds / 29 / 2 ;
    return cm;                  
}

