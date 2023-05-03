import requests

url = "http://localhost:8000/register"
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
headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

print(response.json())
