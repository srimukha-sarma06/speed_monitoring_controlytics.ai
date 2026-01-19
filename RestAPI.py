import requests
import os
from urllib.parse import urljoin

BASE_URL = "http://127.0.0.1:5000"  # Change if running on another host
SAVE_DIR = "downloaded_violations"

# Step 1: Get list of image URLs from the API
response = requests.get(f"{BASE_URL}/api/list-violations")
image_urls = response.json()

# Step 2: Download each image
for url in image_urls:
    img_url = urljoin(BASE_URL, url)
    local_path = os.path.join(SAVE_DIR, *url.split("/")[2:])  # skip /static/
    os.makedirs(os.path.dirname(local_path), exist_ok=True)

    r = requests.get(img_url, stream=True)
    if r.status_code == 200:
        with open(local_path, "wb") as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
        print(f"✅ Downloaded: {local_path}")
    else:
        print(f"❌ Failed: {img_url}")
