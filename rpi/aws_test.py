import os
import boto3
from datetime import datetime

#Initialize s3 client
s3 = boto3.client('s3')

BUCKET_NAME = "htn-test-bucket"
LOCAL_DIR = "/home/gabe/images"

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
	
	for file in files:
		os.remove(os.path.join(LOCAL_DIR, file))

upload_batch()

