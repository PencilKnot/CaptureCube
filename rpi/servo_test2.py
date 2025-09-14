import RPi.GPIO as GPIO
import time

#Pin setup
SERVO1_PIN = 12
SERVO2_PIN = 13
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO1_PIN, GPIO.OUT)
GPIO.setup(SERVO2_PIN, GPIO.OUT)

step_pins = [17, 27, 22, 23]
for pin in step_pins:
	GPIO.setup(pin, GPIO.OUT)
	GPIO.output(pin, 0)
halfstep_seq = [
	[1,0,0,0],
	[1,1,0,0],
	[0,1,0,0],
	[0,1,1,0],
	[0,0,1,0],
	[0,0,1,1],
	[0,0,0,1],
	[1,0,0,1]
]

def step_motor(steps, delay=0.002):
	for i in range(steps):
		seq = halfstep_seq[i%8]
		for pin in range(4):
			GPIO.output(step_pins[pin], seq[pin])
		time.sleep(delay)

pwm = GPIO.PWM(SERVO1_PIN, 50)
pwm2 = GPIO.PWM(SERVO2_PIN, 50)
pwm.start(0)
pwm2.start(5.8)


def rotateStepper():
	steps_per_segment = 341
	for i in range(12):
		print(f"moving segment{i+1}/12")
		step_motor(steps_per_segment)
		print("Pause...")
		time.sleep(2)
	print("Completed full circle")


while(True):
	time_delay = 1


	for i in range(0,31, 1):
		pwm.ChangeDutyCycle(2.5 + (i/180.0)*10)
		pwm2.ChangeDutyCycle(2.5 + ((60-i)/180)*10)
		time.sleep(0.05)
	
	pwm.ChangeDutyCycle(0)
	pwm2.ChangeDutyCycle(0)
	time.sleep(time_delay)
	rotateStepper()
	
	for i in range(31, 61, 1):
		pwm.ChangeDutyCycle(2.5 + (i/180.0)*10)
		pwm2.ChangeDutyCycle(2.5 + ((60-i)/180)*10)
		time.sleep(0.05)

	pwm.ChangeDutyCycle(0)
	pwm2.ChangeDutyCycle(0)
	time.sleep(time_delay)
	rotateStepper()

	for i in range(0, 61, 1):
		pwm.ChangeDutyCycle(2.5 + ((60-i)/180.0)*10)
		pwm2.ChangeDutyCycle(2.5 + (i/180.0)*10)
		time.sleep(0.05)

	pwm.ChangeDutyCycle(0)
	pwm2.ChangeDutyCycle(0)
	time.sleep(time_delay)
	rotateStepper()
