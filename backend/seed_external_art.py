import requests
import random
import os
import sys

BASE_URL = "http://127.0.0.1:8000"

print("1. Logging in to get JWT token...")
login_res = requests.post(f"{BASE_URL}/auth/token", data={
    "username": "tester1",
    "password": "mypassword"
})

if login_res.status_code == 200:
    token = login_res.json()["access_token"]
    print("Login successful.")
else:
    print("Login failed. Ensure the server is running and tester1 is registered.")
    print(login_res.text)
    sys.exit(1)

headers = {"Authorization": f"Bearer {token}"}

print("2. Fetching artworks from Art Institute of Chicago API...")
art_api_url = "https://api.artic.edu/api/v1/artworks?limit=50&fields=id,title,artist_display,image_id"
response = requests.get(art_api_url)

if response.status_code != 200:
    print("Failed to fetch from external API")
    sys.exit(1)

artworks = response.json().get("data", [])

print(f"Fetched {len(artworks)} artworks.")

for art in artworks:
    image_id = art.get("image_id")
    if not image_id:
        continue
    
    title = art.get("title", "Untitled")
    artist = art.get("artist_display", "Unknown Artist")
    price = round(random.uniform(100.0, 5000.0), 2)
    
    print(f"Downloading image for: {title}...")
    img_url = f"https://www.artic.edu/iiif/2/{image_id}/full/843,/0/default.jpg"
    
    try:
        img_res = requests.get(img_url, timeout=10, headers={"User-Agent": "Mozilla/5.0 ArtMarketplace/1.0"})
        if img_res.status_code == 200:
            file_name = f"{image_id}.jpg"
            with open(file_name, "wb") as f:
                f.write(img_res.content)
            
            print(f"Uploading {title} to backend...")
            with open(file_name, "rb") as f:
                upload_res = requests.post(
                    f"{BASE_URL}/artworks/",
                    headers=headers,
                    files={"file": (file_name, f, "image/jpeg")},
                    data={
                        "title": title,
                        "description": artist,
                        "price": str(price)
                    }
                )
            
            if upload_res.status_code == 200:
                print(" -> Success!")
            else:
                print(f" -> Failed to upload: {upload_res.text}")
                
            os.remove(file_name)
        else:
            print(f"Failed to download image {image_id}")
    except Exception as e:
        print(f"Error processing {title}: {e}")

print("3. Fetching artworks from Cleveland Museum of Art API...")
cleveland_api_url = "https://openaccess-api.clevelandart.org/api/artworks/?has_image=1&limit=20"
try:
    response = requests.get(cleveland_api_url)
    if response.status_code == 200:
        c_artworks = response.json().get("data", [])
        print(f"Fetched {len(c_artworks)} artworks from Cleveland API.")
        for art in c_artworks:
            images = art.get("images", {})
            if not images:
                continue
            web_img = images.get("web", {})
            img_url = web_img.get("url")
            if not img_url:
                continue
                
            title = art.get("title", "Untitled")
            
            creators = art.get("creators", [])
            artist = "Unknown Artist"
            if creators and len(creators) > 0:
                artist = creators[0].get("description", "Unknown Artist")
            
            price = round(random.uniform(100.0, 5000.0), 2)
            print(f"Downloading image for: {title}...")
            
            try:
                img_res = requests.get(img_url, timeout=10, headers={"User-Agent": "Mozilla/5.0 ArtMarketplace/1.0"})
                if img_res.status_code == 200:
                    image_id = str(art.get("id", random.randint(100000, 999999)))
                    file_name = f"cma_{image_id}.jpg"
                    with open(file_name, "wb") as f:
                        f.write(img_res.content)
                    
                    print(f"Uploading {title} to backend...")
                    with open(file_name, "rb") as f:
                        upload_res = requests.post(
                            f"{BASE_URL}/artworks/",
                            headers=headers,
                            files={"file": (file_name, f, "image/jpeg")},
                            data={
                                "title": title,
                                "description": artist,
                                "price": str(price)
                            }
                        )
                    
                    if upload_res.status_code == 200:
                        print(" -> Success!")
                    else:
                        print(f" -> Failed to upload: {upload_res.text}")
                        
                    os.remove(file_name)
                else:
                    print(f"Failed to download image {img_url}")
            except Exception as e:
                print(f"Error processing {title}: {e}")
    else:
        print("Failed to fetch from Cleveland API")
except Exception as e:
    print(f"Error connecting to Cleveland API: {e}")

print("Seeding complete!")
