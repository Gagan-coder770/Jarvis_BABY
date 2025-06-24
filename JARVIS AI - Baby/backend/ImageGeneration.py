import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import get_key
import os
import io
from time import sleep

# Function to open an image
def open_image(prompt):
    folder_path = "Data"
    prompt = prompt.replace(" ", "_")
    Files = [f"{prompt}{i}.jpg" for i in range(1, 5)]
    
    for jpg_file in Files:
        image_path = os.path.join(folder_path, jpg_file)
        
        try:
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            sleep(1)
        except IOError:
            print(f"Unable to open {image_path}")

# Get API Key Safely
api_key = get_key(".env", "HuggingFaceAPIKey")
if not api_key:
    print("[ERROR] API Key not found in .env file.")
    exit()

API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {api_key}"}

# Function to call the API asynchronously
async def query(payload):
    try:
        response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
        response.raise_for_status()  # Raise error for bad responses
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] API Request Failed: {e}")
        return None

# Function to generate images
async def generate_images(prompt: str):
    tasks = []
    for _ in range(4):
        payload = {
            "inputs": f"{prompt}, quality=4k, sharpness=maximum, Ultra High details, high resolution, seed = {randint(0, 1000000)}",
        }
        task = asyncio.create_task(query(payload))
        tasks.append(task)

    image_bytes_list = await asyncio.gather(*tasks)

    for i, image_bytes in enumerate(image_bytes_list):
        if image_bytes is None:
            print(f"Skipping image {i+1} due to API failure.")
            continue

        image_path = os.path.join("Data", f"{prompt.replace(' ', '_')}{i + 1}.jpg")
        try:
            img = Image.open(io.BytesIO(image_bytes)) 
            img.save(image_path, "JPEG")
            print(f"Saved image: {image_path}")
        except Exception as e:
            print(f"[ERROR] Failed to save image {i+1}: {e}")

# Wrapper function to run the async generator
def GenerateImages(prompt: str):
    asyncio.run(generate_images(prompt))
    open_image(prompt)

print("Waiting for input in ImageGeneration.data...")

# Continuous Loop to Monitor ImageGeneration.data
while True:
    try:
        data_file = "Frontend/Files/ImageGeneration.data"
        
        if not os.path.exists(data_file):
            print("Waiting for ImageGeneration.data file to be created...")
            sleep(1)
            continue  
        
        with open(data_file, "r") as f:
            Data = f.read().strip()

        if not Data:  
            sleep(1)
            continue

        if "," in Data:
            Prompt, Status = Data.split(",", 1)
            Prompt, Status = Prompt.strip(), Status.strip()
        else:
            print("Invalid data format in ImageGeneration.data. Waiting for valid input...")
            sleep(1)
            continue  

        if Status.lower() == "true":
            print(f"Generating Images for prompt: {Prompt}")
            GenerateImages(prompt=Prompt)

            with open(data_file, "w") as f:
                f.write("False,False")  
        else:
            sleep(1)  
    except Exception as e:
        print(f"Unexpected Error: {e}")
        sleep(1)
