import RPi.GPIO as GPIO
import time

#Pin setup
SERVO1_PIN = 12
SERVO2_PIN = 13
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO1_PIN, GPIO.OUT)
GPIO.setup(SERVO2_PIN, GPIO.OUT)

pwm1 = GPIO.PWM(SERVO1_PIN, 50)
pwm2 = GPIO.PWM(SERVO2_PIN, 50)
pwm1.start(0)
pwm2.start(0)
current_angle1 = 0
current_angle2 = 60

def set_angle1(angle, step=1, delay=0.02):
	global current_angle1
	if angle > current_angle1:
		angles = range(current_angle1, angle + 1, step)
	else:
		angles = range(current_angle1, angle - 1, -step)
	for i in angles:
		duty = 2.5 + (i/180.0)*10
		pwm1.ChangeDutyCycle(duty)
		time.sleep(delay)
	current_angle1 = angle
	pwm1.ChangeDutyCycle(0)

def set_angle2(angle, step=1, delay=0.02):
	global current_angle2
	if angle > current_angle2:
		angles = range(current_angle2, angle + 1, step)
	else:
		angles = range(current_angle2, angle - 1, -step)
	for i in angles:
		duty = 2.5 + (i/180.0)*10
		pwm2.ChangeDutyCycle(duty)
		time.sleep(delay)
	current_angle2 = angle
	pwm2.ChangeDutyCycle(0)

while(True):
	set_angle1(0)
	set_angle2(60)
	time.sleep(3)
	set_angle1(30)
	set_angle2(30)
	time.sleep(3)
	set_angle1(60)
	set_angle2(0)
	time.sleep(3)
