import requests

url = 'http://127.0.0.1:8000/users/1/artworks/'
files = {'file': open(r'C:\Users\jalaj\.gemini\antigravity-ide\brain\31268f2d-d031-43bf-9ead-82a07172b71e\neon_genesis_art_1785963243214.png', 'rb')}
data = {
    'title': 'Neon Genesis',
    'price': '150.00',
    'description': 'A stunning cyberpunk neon cityscape.'
}

response = requests.post(url, files=files, data=data)
print(response.status_code)
print(response.json())
