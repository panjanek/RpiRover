import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import wiringpi2

gpio_enableMotors = 19
gpio_leftPwm = 6
gpio_left1 = 13
gpio_left2 = 12
gpio_rightPwm = 20
gpio_right1 = 16
gpio_right2 = 26

class WebHandler(tornado.web.RequestHandler):
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
    (r'/', WebHandler)
])

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
    stop();
    #enabling motor controller
    wiringpi2.digitalWrite(gpio_enableMotors, 1)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(80)
    tornado.ioloop.IOLoop.instance().start()