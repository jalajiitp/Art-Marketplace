import requests
import uuid

uid = str(uuid.uuid4())[:8]
username = f"test_{uid}"
email = f"test_{uid}@test.com"

# 1. Create a user
print(f"Creating user {username}...")
res = requests.post("http://127.0.0.1:8000/users/", json={"username": username, "email": email, "password": "password"})
print(res.status_code, res.text)

# 2. Login to get token and cookie
print("\nLogging in...")
session = requests.Session()
res = session.post("http://127.0.0.1:8000/auth/token", data={"username": username, "password": "password"})
print(res.status_code, res.json())
print("Cookies:", session.cookies.get_dict())

# 3. Refresh token
print("\nRefreshing token...")
res = session.get("http://127.0.0.1:8000/auth/refresh")
print(res.status_code, res.json())

# 4. Logout
print("\nLogging out...")
res = session.post("http://127.0.0.1:8000/auth/logout")
print(res.status_code, res.json())
print("Cookies:", session.cookies.get_dict())
