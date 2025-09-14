import os 
import subprocess
import pigpio
import RPi.GPIO as GPIO
import time
import boto3
from datetime import datetime

#Initialize s3 client
s3 = boto3.client('s3')

BUCKET_NAME = "htn-test-bucket"
LOCAL_DIR = "/home/gabe/images"

save_path = "/home/gabe/images"
os.makedirs(save_path, exist_ok=True)

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


def rotateStepper(tilt_pos):
	num_images = 12
	delay_between = 0.5
	
	
	steps_per_segment = 341
	for i in range(12):
		print(f"moving segment{i+1}/12")
		step_motor(steps_per_segment)
		#take pic
		filename = os.path.join(save_path, f"{i}{tilt_pos}.jpg")
		cmd = ["fswebcam", "-r", "1280x720", "--jpeg", "85", "-D", "1", "-F", "5", filename]
		result = subprocess.run(cmd, capture_output=True)
		if result.returncode == 0:
			print(f"Image {i}{tilt_pos} saved to {filename}")
		else:
			print("Error capturing image {i}")
			print(result.stderr.decode())
		time.sleep(0.5)
	print("Completed full circle")
	
	
def upload_batch():
	#unique folder name based on timestamp
	folder_name = "run_" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
	
	files = [f for f in os.listdir(LOCAL_DIR) if f.endswith(".jpg")]
	
	for file in files:
		local_path = os.path.join(LOCAL_DIR, file)
		s3_key = f"{folder_name}/{file}" #s3 destination path
		
		print(f"Uploading {local_path} to s3://{BUCKET_NAME}/{s3_key}")
		s3.upload_file(local_path, BUCKET_NAME, s3_key)
		
	print("Batch upload complete")


while(True):
	time_delay = 1


	for i in range(0,31, 1):
		pwm.ChangeDutyCycle(2.5 + (i/180.0)*10)
		pwm2.ChangeDutyCycle(2.5 + ((60-i)/180)*10)
		time.sleep(0.05)
	
	pwm.ChangeDutyCycle(0)
	pwm2.ChangeDutyCycle(0)
	time.sleep(time_delay)
	rotateStepper('a')
	
	for i in range(31, 61, 1):
		pwm.ChangeDutyCycle(2.5 + (i/180.0)*10)
		pwm2.ChangeDutyCycle(2.5 + ((60-i)/180)*10)
		time.sleep(0.05)

	pwm.ChangeDutyCycle(0)
	pwm2.ChangeDutyCycle(0)
	time.sleep(time_delay)
	rotateStepper('b')

	for i in range(0, 61, 1):
		pwm.ChangeDutyCycle(2.5 + ((60-i)/180.0)*10)
		pwm2.ChangeDutyCycle(2.5 + (i/180.0)*10)
		time.sleep(0.05)

	pwm.ChangeDutyCycle(0)
	pwm2.ChangeDutyCycle(0)
	time.sleep(time_delay)
	rotateStepper('c')
	
	
	upload_batch()

