import os 
import subprocess
import pigpio
import time

save_path = "/home/gabe/images"
os.makedirs(save_path, exist_ok=True)

num_images = 5
delay_between = 3

for i in range(1, num_images+1):
    filename = os.path.join(save_path, f"{i}.jpg")
    cmd = ["fswebcam", "-r", "1280x720", "--jpeg", "85", "-D", "1", "-F", "5", filename]
    result = subprocess.run(cmd, capture_output=True)

    if result.returncode == 0:
        print(f"Image {i} saved to {filename}")
    else:
        print("Error capturing image {i}")
        print(result.stderr.decode())
        
