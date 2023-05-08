import requests, base64
from datetime import datetime

access_token='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjozLCJleHAiOjE2ODM1NjMwODR9.H2fUW6e8lR2x4Jj9JAJteRJ9-b0x-s50Sw-SEQBgnZA'
refresh_token='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjozLCJleHAiOjE2ODM2MzYyOTJ9.w2Z9ojLXZ6tNm4eRzPhG2l2pf0Y4VvP8Br_iWwZz7VQ'

# define the API endpoint URL
url = "http://localhost:8000/query_images"

# create a JSON payload with access token and datetime range
dt_from = datetime(2023, 1, 1).isoformat()
dt_to = datetime.now().isoformat()
payload = {
    "access_token": access_token,
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
        with open('query_processed_image_{}.jpg'.format(cnt), 'wb') as f:
            f.write(query_image_data)
        cnt=cnt+1
else:
    print(f"Error: {response.status_code} {response.text}")
