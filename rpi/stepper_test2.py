import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

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


while (True):
	steps_per_segment = 341
	for i in range(12):
		print(f"moving segment{i+1}/12")
		step_motor(steps_per_segment)
		print("Pause...")
		time.sleep(2)
	print("Completed full circle")