import base64
import time
import requests
from google.auth import default
from google.auth.transport.requests import Request
from google.cloud import storage

PROJECT_ID = "your-project-id" 

def image_to_base64(file_path: str) -> str:
    with open(file_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def get_access_token():
    creds, _ = default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    creds.refresh(Request())
    return creds.token

def start_process(access_token, images, prompt):
    image_list = [
        {
            "image": {
                "bytesBase64Encoded": image_to_base64(img),
                "mimeType": "image/jpg"
            },
            "referenceType": "asset"
        }
        for img in images
    ]

    request = {
        "instances": [{
            "prompt": prompt,
            "referenceImages": image_list
        }],
        "parameters": {
            "durationSeconds": 8,
            "storageUri": "gs://{PROJECT_ID}-capture-cube/",
            "sampleCount": 1
        }
    }

    url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/us-central1/publishers/google/models/veo-2.0-generate-exp:predictLongRunning"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    
    response = requests.post(url, headers=headers, json=request)
    
    if not response.ok:
        print(f"Error response: {response.text}")
        print(f"Status code: {response.status_code}")
    
    response.raise_for_status()
    return response.json()["name"]

def status_check(access_token, operation_name):
    url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/us-central1/publishers/google/models/veo-2.0-generate-exp:fetchPredictOperation"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    body = {"operationName": operation_name}
    response = requests.post(url, headers=headers, json=body)
    response.raise_for_status()
    return response.json()

def cont_check(access_token, operation_name):
    while True:
        status = status_check(access_token, operation_name)
        print(f"Status response: {status}")
        
        if status.get("done"):
            videos = status.get("response", {}).get("videos", [])
            if videos:
                return videos[0]
            raise Exception("No video found")
        time.sleep(5)

def generate_video(images, prompt):
    try:
        access_token = get_access_token()
        operation_name = start_process(access_token, images, prompt)
        print("Video generation started.")
        video = cont_check(access_token, operation_name)
        print("Video generation completed.")
        return video
    except Exception as e:
        print("Error during video generation:", e)
        raise

def download_video(gcs_uri, destination_path):
    if not gcs_uri.startswith("gs://"):
        raise ValueError("Invalid?")
    
    parts = gcs_uri[5:].split("/", 1)
    bucket_name = parts[0]
    blob_name = parts[1]
    client = storage.Client(project="{PROJECT_ID}")
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.download_to_filename(destination_path)
    print(f"Video downloaded to {destination_path}")

# testing
if __name__ == "__main__":
    video_info = generate_video(["rotaprint-ui/src/assets/100_7100.JPG", "rotaprint-ui/src/assets/100_7104.JPG", "rotaprint-ui/src/assets/100_7107.JPG"],
                                "Cinematic aerial shot of a grand historical estate at golden hour, with visitors walking through ornate gardens and elegant stone architecture. Camera glides through opulent interior rooms with period furniture, chandeliers, and artwork, then sweeps across manicured grounds with fountains and classical statues. Warm, inviting lighting emphasizes luxury and heritage.")
    print(video_info)
    gcs_uri = video_info.get("gcsUri")
    
    if gcs_uri:
        download_video(gcs_uri, "rotaprint-ui/src/assets/output.mp4")
    else:
        print("No GCS URI found.")