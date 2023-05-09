import requests

# Define the URL of the endpoint
url = "http://localhost:8000/process_video"

# Specify the path to the video file
video_path = "/home/thinkpad/Videos/vdo_1.mp4"

# Open the video file in binary mode and send it in the request
with open(video_path, "rb") as file:
    response = requests.post(url, files={"video": file})

# Check the response status code
if response.status_code == 200:
    # Save the processed video file
    with open("/home/thinkpad/temp/processed_video.mp4", "wb") as file:
        file.write(response.content)
else:
    print("Request failed with status code:", response.status_code)
