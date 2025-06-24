from frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus
)

from backend.model import FirstLayerDMM
from backend.RealtimesearchEngine import RealtimeSearchEngine
from backend.automation import process_command
from backend.SpeechToText import SpeechRecognition
from backend.chatbot import ChatBot
from backend.TextTospeech import TextToSpeech, play_audio 
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import os

env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
DefaultMessage = f'''{Username} : Hello {Assistantname}! How are you?
{Assistantname} : Hello {Username} I'm doing well, how can I help you today?
'''
subprocesses = []
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]

def ShowDefaultChatIfNoChats():
    try:
        with open(r"Data\ChatLog.json", "r", encoding="utf-8") as file:
            if len(file.read()) < 5:
                with open(TempDirectoryPath("Database.data"), "w", encoding="utf-8") as f:
                    f.write("")
                with open(TempDirectoryPath("Responses.data"), "w", encoding="utf-8") as f:
                    f.write(DefaultMessage)
    except FileNotFoundError:
        print("⚠️ Warning: ChatLog.json not found.")


def ReadChatLogJson():
    try:
        with open(r"Data\ChatLog.json", "r", encoding="utf-8") as file:
            data = file.read().strip()
            return json.loads(data) if data else []
    except (FileNotFoundError, json.JSONDecodeError):
        print("⚠️ Warning: ChatLog.json is missing or corrupted. Resetting file.")
        with open(r"Data\ChatLog.json", "w", encoding="utf-8") as file:
            json.dump([], file)
        return []


def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = "\n".join(
        f"{Username if entry['role'] == 'user' else Assistantname}: {entry['content']}"
        for entry in json_data
    )
    with open(TempDirectoryPath("Database.data"), "w", encoding="utf-8") as file:
        file.write(AnswerModifier(formatted_chatlog))


def ShowChatsOnGUI():
    try:
        with open(TempDirectoryPath("Database.data"), "r", encoding="utf-8") as file:
            data = file.read()
        if data:
            with open(TempDirectoryPath("Responses.data"), "w", encoding="utf-8") as file:
                file.write(data)
    except FileNotFoundError:
        print("⚠️ Warning: Database.data not found.")


def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()

InitialExecution()


def MainExecution():
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""

    SetAssistantStatus("Listening...")
    Query = SpeechRecognition()
    ShowTextToScreen(f"{Username} : {Query}")
    SetAssistantStatus("Thinking...")
    classifier = FirstLayerDMM()  # Instantiate the class
    Decision = [classifier(Query)]  # Call it as a function

    print(f"\nDecision: {Decision}\n")

    G = any(i.startswith("general") for i in Decision)
    R = any(i.startswith("realtime") for i in Decision)

    Merged_query = " and ".join(
        " ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")
    )

    for queries in Decision:
        if "generate " in queries:
            ImageGenerationQuery = str(queries)
            ImageExecution = True

    for queries in Decision:
        if not TaskExecution and any(queries.startswith(func) for func in Functions):
            run(process_command(queries))  # ✅ Pass as a string, not a list
            TaskExecution = True

    if ImageExecution:
        with open(r"Frontend\Files\ImageGeneration.data", "w") as file:
            file.write(f"{ImageGenerationQuery},True")
        try:
            p1 = subprocess.Popen(["python", r"Backend\ImageGeneration.py"],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  stdin=subprocess.PIPE, shell=False)
            subprocesses.append(p1)
        except Exception as e:
            print(f"Error Generating Image: {e}")

    if G and R or R:
        SetAssistantStatus("Searching...")
        Answer = RealtimeSearchEngine(QueryModifier(Merged_query))
    else:
        for Queries in Decision:
            if "general " in Queries:
                QueryFinal = Queries.replace("general ", "")
                Answer = ChatBot(QueryModifier(QueryFinal))
                break
            elif "realtime " in Queries:
                QueryFinal = Queries.replace("realtime ", "")
                Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
                break
        else:
            return

    ShowTextToScreen(f"{Assistantname} : {Answer}")
    SetAssistantStatus("Answering...")
    TextToSpeech(Answer)
    play_audio()
    return True


def FirstThread(): 
    while True:
        try:
            if GetMicrophoneStatus() == "True":
                MainExecution()
        except Exception as e:
            print(f"⚠️ Error in FirstThread: {e}")
        else:
            if GetAssistantStatus() != "Available...":
                SetAssistantStatus("Available...")
        sleep(0.1)


def SecondThread():
    GraphicalUserInterface()


if __name__ == "__main__":
    threading.Thread(target=FirstThread, daemon=True).start()
    SecondThread()
