
import asyncio
import base64
import os
import sys

# Add app to path to import services
sys.path.append(os.getcwd())

from app.services.baidu_ai import baidu_ai_service
from app.config import get_settings

# Overwrite settings to ensure we use what's in the environment or .env
# But get_settings() should load from .env automatically if python-dotenv is used.
# Let's assume the environment is set up correctly when running the script.

IMAGE_PATH = r"C:/Users/17160/.gemini/antigravity/brain/1cc3f5b5-05be-43c2-986b-566885a54513/uploaded_media_0_1769692244109.png"

async def main():
    print(f"Testing Baidu AI with image: {IMAGE_PATH}")
    
    if not os.path.exists(IMAGE_PATH):
        print("Image file not found!")
        return

    with open(IMAGE_PATH, "rb") as f:
        image_bytes = f.read()
    
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    
    print("Sending request to Baidu AI...")
    try:
        results = await baidu_ai_service.recognize_dish(image_base64)
        print("\n--- Recognition Results ---")
        for res in results:
            print(f"Name: {res.name}, Confidence: {res.confidence}, Category: {res.category}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
