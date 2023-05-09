import requests, json

url = "http://localhost:8000/register"
url2 = "http://localhost:8000/login"
payload = {
    "user_name": "",
    "email": "",
    "password": "mypassword"
}
payload2 = {
    "user_name": "surachai",
    "email": "sura@example.com",
    "password": "mypassword",
    "api_quota_limit": 200
}
payload3 = {
    "email": "sura@example.com",
    "password": "mypassword",
}
headers = {
    "Content-Type": "application/json"
}

regis_messi = {
    "user_name": "lionel_messi",
    "email": "messi@test.com",
    "password": "messi_pass",
    "api_quota_limit": 200
}
payload_messi = {
    "email": "messi@test.com",
    "password": "messi_pass",
}

regis_ronaldo = {
    "user_name": "ronaldo",
    "email": "ronaldo@test.com",
    "password": "ronaldo_pass",
    "api_quota_limit": 200
}
payload_ronaldo = {
    "email": "ronaldo@test.com",
    "password": "ronaldo_pass",
}

response = requests.post(url, json=regis_ronaldo, headers=headers)
#response = requests.post(url2, json=payload_messi, headers=headers)

print(response.json())

# # Serializing json
# json_object = json.dumps(response.json()['detail'], indent=4)
 
# # Writing to sample.json
# with open("/home/thinkpad/temp/key.json", "w") as outfile:
#     outfile.write(json_object)