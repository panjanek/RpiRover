# RpiRover
Raspberry Pi Rover with web interface

# Hardware parts

 - Raspberry Pi 2
 - Motor driver TB6612FNG: (Pololu #713)
 - Ultrasonic distance sensor HC-SR04 mounted on microservo
 - TIP120 Darlington Transistor + 470Ohm resistor 
 - Short LED strip (front lights)
 - Arduino Nano
 - Robby RP5/RP6 Arexx Chassis with two DC motors
 - USB Camera
 - USB WiFi Dongle
 - Step-Down voltage regulator D15V35F5S3 (Pololu #2110)

# Software parts

 - Python script server.py serving web page and handling websocket communication (controll commands)
 - Arduino sketch rover.ino for distance measurement, controlling servo and serial port communication
 - Motion deamon for streaming camera video ofer HTTP as mjpg stream
