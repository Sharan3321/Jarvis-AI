from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os

# Load environment variables
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

# User-agent for web scraping
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

# Initialize Groq client
client = Groq(api_key=GroqAPIKey)

# Professional responses (unused currently but kept as per original code)
professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need—don't hesitate to ask.",
]

# AI system initialization
messages = []
SystemChatBot = [{"role": "system", "content": "You're a content writer. You have to write content like letters."}]


def GoogleSearch(Topic):
    search(Topic)
    return True


def Content(Topic):
    def OpenNotepad(File):
        # Open the file in Notepad
        default_text_editor = 'Notepad.exe'
        subprocess.Popen([default_text_editor, File])

    def ContentWriterAI(prompt):
        # Append user prompt to the conversation
        messages.append({"role": "user", "content": f"{prompt}"})

        try:
            # Generate content using Groq API
            completion = client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=SystemChatBot + messages,
                max_tokens=2048,
                temperature=0.7,
                top_p=1,
                stream=False,
                stop=None
            )
            Answer = completion['choices'][0]['message']['content']
            Answer = Answer.replace("</s>", "")
            # Append assistant's response to messages
            messages.append({"role": "assistant", "content": Answer})
            return Answer
        except Exception as e:
            print(f"Error generating content: {e}")
            return "Failed to generate content. Please check the API or try again later."

    # Clean the topic input
    Topic = Topic.replace("Content ", "").strip()

    # Generate content
    ContentByAI = ContentWriterAI(Topic)

    # Ensure Data directory exists
    os.makedirs("Data", exist_ok=True)
    file_path = rf"Data\{Topic.lower().replace(' ', '_')}.txt"

    try:
        # Write content to a file
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(ContentByAI)
        print(f"Content saved to: {file_path}")

        # Open the file in Notepad
        OpenNotepad(file_path)
    except Exception as e:
        print(f"Error writing to file: {e}")

    return True



def YouTubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(Url4Search)
    return True



def PlayYoutube(query):
    playonyt(query)
    return True
    


def OpenApp(app, sess=requests.session()):
    try:
        # Attempt to open the app using AppOpener
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        # Perform a fallback search if AppOpener fails
        def extract_links(html):
            if html is None:
                return []
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all('a', {'jsname': 'UWckNb'})
            return [link.get('href') for link in links]

        def search_google(query):
            url = f"https://www.google.com/search?q={query}"
            headers = {"User-Agent": useragent}
            response = sess.get(url, headers=headers)
            return response.text if response.status_code == 200 else None

        html = search_google(app)
        if html:
            links = extract_links(html)
            if links:
                webopen(links[0])
        return True



def CloseApp(app):
    if "chrome" in app:
        # Skip closing Chrome
        return False
    else:
        try:
            close(app, match_closest=True, output=True, throw_error=True)
            return True
        except Exception as e:
            print(f"Error closing app: {e}")
            return False


def System(command):
    def mute():
        keyboard.press_and_release("volume mute")

    def unmute():
        keyboard.press_and_release("volume unmute")

    def volume_up():
        keyboard.press_and_release("volume up")

    def volume_down():
        keyboard.press_and_release("volume down")

    if command == "mute":
        mute()
    elif command == "unmute":
        unmute()
    elif command == "volume up":
        volume_up()
    elif command == "volume down":
        volume_down()

    return True


async def TranslateAndExecute(commands: list[str]):
    funcs = []

    for command in commands:
        if command.startswith("open "):
            funcs.append(asyncio.to_thread(OpenApp, command.removeprefix("open ")))

        elif command.startswith("close "):
            funcs.append(asyncio.to_thread(CloseApp, command.removeprefix("close ")))

        elif command.startswith("play "):
            funcs.append(asyncio.to_thread(PlayYoutube, command.removeprefix("play ")))

        elif command.startswith("content "):
            funcs.append(asyncio.to_thread(Content, command.removeprefix("content ")))

        elif command.startswith("google search "):
            funcs.append(asyncio.to_thread(GoogleSearch, command.removeprefix("google search ")))

        elif command.startswith("youtube search "):
            funcs.append(asyncio.to_thread(YouTubeSearch, command.removeprefix("youtube search ")))

        elif command.startswith("system "):
            funcs.append(asyncio.to_thread(System, command.removeprefix("system ")))

        else:
            print(f"No function found for: {command}")

    results = await asyncio.gather(*funcs)
    for result in results:
        yield result


async def Automation(commands: list[str]):
    async for result in TranslateAndExecute(commands):
        pass
    return True
if __name__ == "__main__":
    asyncio.run(Automation(["open facebook", "open instagram", "open telegram", "play perfect","content song for me"]))
