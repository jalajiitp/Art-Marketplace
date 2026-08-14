import requests
import sys

BASE_URL = "http://127.0.0.1:8000"

print("1. Registering user...")
reg_res = requests.post(f"{BASE_URL}/users/", json={
    "username": "tester1",
    "email": "test@test.com",
    "password": "mypassword"
})
if reg_res.status_code == 200:
    print("User registered successfully.")
else:
    print("User registration issue (might exist):", reg_res.json())

print("2. Logging in...")
login_res = requests.post(f"{BASE_URL}/auth/token", data={
    "username": "tester1",
    "password": "mypassword"
})
if login_res.status_code == 200:
    token = login_res.json()["access_token"]
    print("Login successful, obtained JWT.")
else:
    print("Login failed:", login_res.json())
    sys.exit(1)

print("3. Uploading artwork...")
headers = {"Authorization": f"Bearer {token}"}
with open("test.jpg", "rb") as f:
    files = {"file": f}
    data = {
        "title": "Auth Test Art",
        "price": "500",
        "description": "Art uploaded using JWT token"
    }
    upload_res = requests.post(f"{BASE_URL}/artworks/", headers=headers, files=files, data=data)

if upload_res.status_code == 200:
    print("Upload successful!")
    print(upload_res.json())
else:
    print("Upload failed:", upload_res.json())
