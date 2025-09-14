import cv2
import os
from datetime import datetime

# Directory to save the image
save_dir = "/home/gabe/images"

# Ensure the directory exists
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# Open the webcam (0 is the default camera)
cap = cv2.VideoCapture(0)

# Check if the webcam opened correctly
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# Set the resolution (you can change these values)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Set width to 640
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # Set height to 480

# Capture a single frame
ret, frame = cap.read()

# Check if the frame was captured correctly
if not ret:
    print("Failed to capture image.")
    cap.release()
    exit()

# Get the current timestamp for a unique filename
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
image_filename = f"{save_dir}/image_{timestamp}.jpg"

# Save the captured image
cv2.imwrite(image_filename, frame)

# Release the webcam (important to stop the feed properly)
cap.release()

# Output the file path of the saved image
print(f"Image saved as {image_filename}")
