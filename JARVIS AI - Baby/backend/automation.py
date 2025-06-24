import os
import subprocess
import webbrowser
import requests
import asyncio
import keyboard
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
from pywhatkit import search, playonyt
from AppOpener import close, open as appopen
from AppOpener import open as appopen

def process_command(command: str):
    command = command.lower().strip()
    
    if command.startswith("google search"):
        topic = command.replace("google search", "").strip()
        if topic:
            search(topic)
            print(f"Searching Google for: {topic}")
        else:
            print("Please specify a topic to search on Google.")
    
    elif command.startswith("youtube search"):
        topic = command.replace("youtube search", "").strip()
        if topic:
            playonyt(topic)
            print(f"Playing top YouTube video for: {topic}")
        else:
            print("Please specify a topic to search on YouTube.")
    
    elif command.startswith("open"):
        app_name = command.replace("open", "").strip()
        if app_name:
            try:
                subprocess.Popen([app_name])
                print(f"Opening {app_name}...")
            except FileNotFoundError:
                print(f"{app_name} not found. Searching online...")
                webbrowser.open(f"https://www.google.com/search?q={app_name}+download")
        else:
            print("Please specify an application to open.")
    
    else:
        print("Command not recognized. Try 'Google search', 'YouTube search', or 'Open'.")




def open_app(app_name):
    try:
        # Try opening with AppOpener
        appopen(app_name)
        print(f"Opening {app_name}...")
    except Exception as e:
        try:
            # Try opening with 'start' command
            os.system(f"start {app_name}")
        except:
            try:
                # Try opening with subprocess (provide full path for known apps)
                app_paths = {
                    "spotify": r"C:\Users\YourUsername\AppData\Roaming\Spotify\Spotify.exe",
                    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                }
                if app_name in app_paths:
                    subprocess.Popen([app_paths[app_name]])
                else:
                    print(f"Could not find the full path for {app_name}.")
            except Exception as e:
                print(f"Error launching {app_name}: {e}")

# Example Usage
open_app("")


# Load environment variables
env_vars = dotenv_values(".env")
GROQ_API_KEY = env_vars.get("GROQ_API_KEY", "")
client = Groq(api_key=GROQ_API_KEY)

# Function to perform a Google search
def GoogleSearch(topic):
    search(topic)
    return True

# Function to generate and save AI-generated content
def ContentWriterAI(prompt):
    messages = [{"role": "user", "content": prompt}]
    completion = client.chat(messages)
    
    answer = "".join(chunk.choices[0].delta.content for chunk in completion if chunk.choices[0].delta.content)
    return answer.replace("</s>", "")


def Content(topic):
    topic = topic.replace("Content ", "").strip()
    content_text = ContentWriterAI(topic)
    file_path = rf"Data\\{topic.lower().replace(' ', '')}.txt"
    
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content_text)
    
    OpenNotepad(file_path)
    return True

def OpenNotepad(file):
    subprocess.Popen(["notepad.exe", file])


def PlayYoutube(query):
    playonyt(query)
    return True


def OpenApp(app):
    try:
        if app.lower() == "chrome":
            subprocess.Popen([r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            os.system(f"start {app}")
        return True
    except Exception as e:
        print(f"Error launching {app}: {e}")
        return False


def extract_links(html):
    if html is None:
        return []
    soup = BeautifulSoup(html, 'html.parser')
    links = [link.get('href') for link in soup.find_all('a', {'class': 'yuRUbf'})]
    return links


def search_google(query):
    url = f"https://www.google.com/search?q={query}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.text
    else:
        print("Failed to retrieve search results.")
        return None


def CloseApp(app):
    if "chrome" in app:
        return False
    try:
        close(app, match_closest=True, output=True, throw_error=True)
    except:
        return False
    return True


def System(command):
    actions = {
        "mute": lambda: keyboard.press_and_release("volume mute"),
        "unmute": lambda: keyboard.press_and_release("volume mute"),
        "volume up": lambda: keyboard.press_and_release("volume up"),
        "volume down": lambda: keyboard.press_and_release("volume down")
    }
    actions.get(command, lambda: print("Invalid command"))()
    return True


async def TranslateAndExecute(commands: list[str]):
    funcs = []
    for command in commands:
        if command.startswith("open "):
            funcs.append(asyncio.to_thread(OpenApp, command.replace("open ", "")))
        elif command.startswith("close "):
            funcs.append(asyncio.to_thread(CloseApp, command.replace("close ", "")))
        elif command.startswith("play "):
            funcs.append(asyncio.to_thread(PlayYoutube, command.replace("play ", "")))
        elif command.startswith("system "):
            funcs.append(asyncio.to_thread(System, command.replace("system ", "")))
    
    results = await asyncio.gather(*funcs)
    for result in results:
        yield result


async def Automation(commands: list[str]):
    async for result in TranslateAndExecute(commands):
        pass
    return True
