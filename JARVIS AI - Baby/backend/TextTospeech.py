import pygame
import random
import asyncio
import edge_tts
import os
from dotenv import dotenv_values
import threading  # For multi-threading

VOICE = "en-AU-WilliamNeural"     # YOU CAN CHANGE THIS VOICE ACCORDING TO YOU

# Load environment variables from a .env file
env_vars = dotenv_values(".env")

# Your Assistant Voice (default to a valid string if not found in .env)
AssistantVoice = env_vars.get("AssistantVoice", "en-CA-liamNeural")

# Ensure AssistantVoice is a string
if not isinstance(AssistantVoice, str) or not AssistantVoice:
    raise ValueError("AssistantVoice must be a valid string.")

# Asynchronous function to convert text to an audio file
async def TextToAudioFile(text):
    file_path = r"Data\\speech.mp3"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    if os.path.exists(file_path):
        os.remove(file_path)
    print("Generating audio...")
    communicate = edge_tts.Communicate(text, AssistantVoice, pitch='+5Hz', rate='+13%')
    await communicate.save(file_path)
    print(f"Audio file saved: {file_path}")
    return file_path

def remove_file(file_path):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Removed file: {file_path}")
    except Exception as e:
        print(f"Error removing file: {e}")

# Function to manage Text-to-Speech (TTS) functionality
def TTS(Text, func=lambda r=None: True):
    pygame.mixer.init()
    try:
        file_path = asyncio.run(TextToAudioFile(Text))
        if os.path.exists(file_path):
            print("File exists, attempting playback...")
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
        else:
            print(f"Error: File {file_path} not found.")
    except Exception as e:
        print(f"Error during TTS: {e}")
    finally:
        pygame.mixer.quit()

# Function to manage Text-to-Speech with additional responses for long text
def TextToSpeech(Text, func=lambda x=None: True):
    Data = str(Text).split(".")  # Split the text by periods into a list of sentences

    # List of predefined responses for cases where the text is too long
    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        "The remaining part of the text is now on the chat screen, sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, sir.",
        "Sir, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, sir.",
        "The next part of the text is on the chat screen, sir.",
        "Sir, please check the chat screen for more information.",
        "There's more text on the chat screen for you, sir.",
        "Sir, take a look at the chat screen for additional text.",
        "You'll find more to read on the chat screen, sir.",
        "Sir, check the chat screen for the rest of the text.",
        "The chat screen has the rest of the text, sir.",
        "There's more to see on the chat screen, sir, please look.",
        "Sir, the chat screen holds the continuation of the text.",
        "You'll find the complete answer on the chat screen, kindly check it out sir.",
        "Please review the chat screen for the rest of the text, sir.",
        "Sir, look at the chat screen for the complete answer."
    ]

    # If the text is very long (more than 4 sentences and 250 characters), add a response message
    if len(Data) > 4 and len(Text) > 250:
        TTS(" ".join(Text.split(".")[0:2]) + ". " + random.choice(responses), func)
    # Otherwise, just play the whole text
    else:
        TTS(Text, func)

# Async function to generate TTS
async def generate_tts(TEXT, output_file):
    try:
        print("\033[92mGenerating TTS...\033[0m")  # Green text
        communicate = edge_tts.Communicate(TEXT, VOICE)
        await communicate.save(output_file)
        print("\033[94mTTS Generation Complete.\033[0m")  # Blue text
    except Exception as e:
        print(f"\033[91mError during TTS generation: {e}\033[0m")  # Red text

def play_audio(file_path):
    print("\033[92mPlaying audio...\033[0m")  # Green text
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.mixer.quit()

# Function to handle TTS and playback using threads
def speak(TEXT):
    output_file = "output.mp3"
    # Thread for TTS generation
    tts_thread = threading.Thread(target=lambda: asyncio.run(generate_tts(TEXT, output_file)))
    tts_thread.start()
    tts_thread.join()  # Wait for TTS to finish

    # Thread for audio playback
    if os.path.exists(output_file):
        play_thread = threading.Thread(target=play_audio, args=(output_file,))
        play_thread.start()
        play_thread.join()

    # Clean up the file
    remove_file(output_file)

# Main execution loop
if __name__ == "__main__":
    while True:
        try:
            TextToSpeech(input("Enter the text: "))
        except KeyboardInterrupt:
            print("\nExiting...")
            break

