import requests, base64, json

def add2quotation(msg):
    return ('\"'+msg+'\"')

# Opening JSON file
f = open('/home/thinkpad/temp/key_ronaldo.json')
  
# returns JSON object as 
# a dictionary
key = json.load(f)
  
# Closing file
f.close()

# Define the endpoint URL
endpoint_url = 'http://localhost:8000/process_image'

mypath = '/home/thinkpad/Pictures/ronaldo/'

from os import listdir
from os.path import isfile, join
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

# print(onlyfiles)

cnt=0
for fname in onlyfiles:
    # Open the image file and read the data into memory
    with open(mypath+fname, 'rb') as f:
        image_data = f.read()

    # Encode the image data as a base64 string
    image_b64 = base64.b64encode(image_data).decode('utf-8')
    #image_b64=add2quotation(image_b64)
    #access_token=add2quotation(access_token)
    #print("access_token : ", access_token)

    payload = {"image_b64":image_b64,
            "access_token":key['access_token']}

    # Send the image data to the endpoint using a POST request
    response = requests.post(endpoint_url, json=payload)

    # Check the response status code and content
    if response.status_code == 200:
        # Extract the processed image data from the response JSON
        processed_image_b64 = response.json()['image_b64']
        
        # Decode the processed image data from base64 to bytes
        processed_image_data = base64.b64decode(processed_image_b64)
        
        # Save the processed image data to a file
        with open('/home/thinkpad/temp/processed_image_{}.jpg'.format(cnt), 'wb') as f:
            f.write(processed_image_data)
    else:
        # Handle errors or other response codes as needed
        print('Error:', response.status_code, response.content)
    cnt=cnt+1

