import requests, base64, json
from datetime import datetime

# Opening JSON file
f = open('/home/thinkpad/temp/key_ronaldo.json')
  
# returns JSON object as 
# a dictionary
key = json.load(f)
  
# Closing file
f.close()

# define the API endpoint URL
url = "http://localhost:8000/query_images"

# create a JSON payload with access token and datetime range
dt_from = datetime(2023, 1, 1).isoformat()
dt_to = datetime.now().isoformat()
payload = {
    "access_token": key['access_token'],
    "dt_from": dt_from,
    "dt_to": dt_to
}

# send the POST request with the JSON payload
response = requests.post(url, json=payload)

# check the response status code and content
if response.status_code == 200:
    image_b64s = response.json()
    # do something with the returned image_b64s
    #print(base64.b64decode(image_b64s[0]))
    cnt=0
    for img in image_b64s:
        # Decode the processed image data from base64 to bytes
        query_image_data = base64.b64decode(img)
        
        # Save the processed image data to a file
        with open('/home/thinkpad/temp/query_processed_image_{}.jpg'.format(cnt), 'wb') as f:
            f.write(query_image_data)
        cnt=cnt+1
else:
    print(f"Error: {response.status_code} {response.text}")
