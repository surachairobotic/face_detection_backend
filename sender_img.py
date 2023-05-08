import requests
import base64

def add2quotation(msg):
    return ('\"'+msg+'\"')

access_token='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjozLCJleHAiOjE2ODM1NjMwODR9.H2fUW6e8lR2x4Jj9JAJteRJ9-b0x-s50Sw-SEQBgnZA'
refresh_token='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjozLCJleHAiOjE2ODM2MzYyOTJ9.w2Z9ojLXZ6tNm4eRzPhG2l2pf0Y4VvP8Br_iWwZz7VQ'

# Define the endpoint URL
endpoint_url = 'http://localhost:8000/process_image'

# Open the image file and read the data into memory
with open('/home/thinkpad/Pictures/face2.jpg', 'rb') as f:
    image_data = f.read()

# Encode the image data as a base64 string
image_b64 = base64.b64encode(image_data).decode('utf-8')
#image_b64=add2quotation(image_b64)
#access_token=add2quotation(access_token)
#print("access_token : ", access_token)

payload = {"image_b64":image_b64,
           "access_token":access_token}

# Send the image data to the endpoint using a POST request
response = requests.post(endpoint_url, json=payload)

# Check the response status code and content
if response.status_code == 200:
    # Extract the processed image data from the response JSON
    processed_image_b64 = response.json()['image_b64']
    
    # Decode the processed image data from base64 to bytes
    processed_image_data = base64.b64decode(processed_image_b64)
    
    # Save the processed image data to a file
    with open('processed_image.jpg', 'wb') as f:
        f.write(processed_image_data)
else:
    # Handle errors or other response codes as needed
    print('Error:', response.status_code, response.content)

