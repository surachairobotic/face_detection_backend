import requests

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

#response = requests.post(url, json=payload2, headers=headers)
response = requests.post(url2, json=payload3, headers=headers)

print(response.json())

