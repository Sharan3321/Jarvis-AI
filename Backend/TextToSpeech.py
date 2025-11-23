import pygame
import random
import asyncio
import edge_tts
import os
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice", "en-US-JennyNeural")  # Default voice if not provided

async def TextToAudioFile(text) -> None:
    """
    Converts text to an audio file using edge_tts.
    """
    file_path = r"Data/speech.mp3"

    # Remove the file if it already exists
    if os.path.exists(file_path):
        os.remove(file_path)

    try:
        # Create an audio file using edge_tts
        communicate = edge_tts.Communicate(text, voice=AssistantVoice, pitch="+5Hz", rate="+13%")
        await communicate.save(file_path)
    except Exception as e:
        print(f"Error in TextToAudioFile: {e}")
        raise e  # Rethrow the exception for debugging purposes

def TTS(Text, func=lambda r=None: True):
    """
    Converts text to speech and plays it using pygame.
    """
    try:
        # Convert text to audio file asynchronously
        asyncio.run(TextToAudioFile(Text))

        # Initialize pygame mixer and play the generated audio file
        pygame.mixer.init()
        pygame.mixer.music.load(r"Data/speech.mp3")
        pygame.mixer.music.play()

        # Wait until the playback finishes or the callback indicates to stop
        while pygame.mixer.music.get_busy():
            if not func():
                pygame.mixer.music.stop()
                break
            pygame.time.Clock().tick(10)  # Prevent high CPU usage

        return True
    except Exception as e:
        print(f"Error in TTS: {e}")
        return False
    finally:
        try:
            # Cleanup pygame mixer
            func(False)
            if pygame.mixer.get_init():  # Check if mixer is initialized
                pygame.mixer.music.stop()
                pygame.mixer.quit()
        except Exception as e:
            print(f"Error in finally block: {e}")

def TextToSpeech(Text, func=lambda r=None: True):
    """
    Breaks text into smaller parts and converts to speech if necessary.
    """
    # Split text into sentences
    Data = str(Text).split(".")

    # List of responses for truncating large text
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
    ]

    if len(Data) > 4 and len(Text) > 250:
        # Play the first two sentences and add a random response
        first_part = " ".join(Data[:2]) + "."
        response = random.choice(responses)
        TTS(first_part + " " + response, func)
    else:
        # Play the full text
        TTS(Text, func)

if __name__ == "__main__":
    try:
        # Main loop to accept user input and convert to speech
        while True:
            user_input = input("Enter the text: ").strip()
            if user_input.lower() in ["exit", "quit"]:
                print("Exiting...")
                break
            TextToSpeech(user_input)
    except KeyboardInterrupt:
        print("\nExiting...")


