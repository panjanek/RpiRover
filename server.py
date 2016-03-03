import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import wiringpi2
import serial
import time
import os

gpio_enableMotors = 19
gpio_leftPwm = 6
gpio_left1 = 13
gpio_left2 = 12
gpio_rightPwm = 20
gpio_right1 = 16
gpio_right2 = 26
gpio_lights = 23
serialport = '/dev/ttyUSB0'
ser = None

class WebStaticFileHandler(tornado.web.StaticFileHandler):
    def set_extra_headers(self, path):
        # Disable cache
        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("public/index.html")

class WSHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print 'New connection was opened'
	  
    def on_message(self, message):
        print 'Incoming message:', message
        if message == "stop":
            stop()
        elif message == "left":
            left()
        elif message == "right":
            right()
        elif message == "forward":
            forward()
        elif message == "backward":
            backward()
        elif message == "lightson":
            wiringpi2.digitalWrite(gpio_lights, 1)
        elif message == "lightsoff":
            wiringpi2.digitalWrite(gpio_lights, 0)
        elif message == "reboot":
            stop() 		
            os.system("/sbin/reboot")
        elif message == "shutdown":
            stop()		
            os.system("/sbin/shutdown -h -H now")			
        elif message == "distance":
            serialCommand("D;")
            time.sleep(0.05)
            out = ''
            if ser is not None:
                while ser.inWaiting() > 0:
                    out += ser.read(1)
            self.write_message(out)				
        else:
            split =  message.split(' ');
            if split[0] == 'servo':
                angle = split[1]
                cmd = "S" + angle + ";"
                serialCommand(cmd)

    def on_close(self):
        print 'Connection was closed...'
		
def stop():
    wiringpi2.digitalWrite(gpio_left1, 0)
    wiringpi2.digitalWrite(gpio_left2, 0)
    wiringpi2.digitalWrite(gpio_leftPwm, 0)
    wiringpi2.digitalWrite(gpio_right1, 0)
    wiringpi2.digitalWrite(gpio_right2, 0)	
    wiringpi2.digitalWrite(gpio_rightPwm, 0)	
   
def forward():  
    wiringpi2.digitalWrite(gpio_left1, 0)
    wiringpi2.digitalWrite(gpio_left2, 1)
    wiringpi2.digitalWrite(gpio_leftPwm, 1)
    wiringpi2.digitalWrite(gpio_right1, 0)
    wiringpi2.digitalWrite(gpio_right2, 1)	
    wiringpi2.digitalWrite(gpio_rightPwm, 1)	
	
def backward():  
    wiringpi2.digitalWrite(gpio_left1, 1)
    wiringpi2.digitalWrite(gpio_left2, 0)
    wiringpi2.digitalWrite(gpio_leftPwm, 1)
    wiringpi2.digitalWrite(gpio_right1, 1)
    wiringpi2.digitalWrite(gpio_right2, 0)	
    wiringpi2.digitalWrite(gpio_rightPwm, 1)

def left():  
    wiringpi2.digitalWrite(gpio_left1, 1)
    wiringpi2.digitalWrite(gpio_left2, 0)
    wiringpi2.digitalWrite(gpio_leftPwm, 1)
    wiringpi2.digitalWrite(gpio_right1, 0)
    wiringpi2.digitalWrite(gpio_right2, 1)	
    wiringpi2.digitalWrite(gpio_rightPwm, 1)	

def right():  
    wiringpi2.digitalWrite(gpio_left1, 0)
    wiringpi2.digitalWrite(gpio_left2, 1)
    wiringpi2.digitalWrite(gpio_leftPwm, 1)
    wiringpi2.digitalWrite(gpio_right1, 1)
    wiringpi2.digitalWrite(gpio_right2, 0)	
    wiringpi2.digitalWrite(gpio_rightPwm, 1)
	
application = tornado.web.Application([
    (r'/ws', WSHandler),
	(r'/', MainHandler),
	(r'/tmp/(.*)', WebStaticFileHandler, {"path": "/tmp"}),
	(r'/(.*)', WebStaticFileHandler, {"path": "/home/pi/RpiRover/public"})
])

def serialCommand(cmd):
    global ser
    if ser is None:
        try:
            ser = serial.Serial(port=serialport,baudrate=9600, timeout=1)
        except:
            ser = None
            print "Error opening serial port"
    try:
        ser.write(cmd)
    except:
        print "Error sending data to serial port"	
        try:
            ser.close()
        except:
            print "Error closing port"
        ser = None
		

if __name__ == "__main__":
    wiringpi2.wiringPiSetupGpio()  # BCM numeration
    #motors pins set to output
    wiringpi2.pinMode(gpio_enableMotors, 1)
    wiringpi2.pinMode(gpio_leftPwm, 1)
    wiringpi2.pinMode(gpio_left1, 1)
    wiringpi2.pinMode(gpio_left2, 1)
    wiringpi2.pinMode(gpio_rightPwm, 1)
    wiringpi2.pinMode(gpio_right1, 1)
    wiringpi2.pinMode(gpio_right2, 1)
    wiringpi2.pinMode(gpio_lights, 1)
    stop();
    #enabling motor controller
    wiringpi2.digitalWrite(gpio_enableMotors, 1)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(80)
    tornado.ioloop.IOLoop.instance().start()