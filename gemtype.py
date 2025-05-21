import os
import threading
import pyautogui
import pyperclip
import keyboard
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Get API key securely
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("❌ GEMINI_API_KEY not found. Set it in your .env file.")
    exit(1)

model = "gemini-2.5-flash-preview-05-20"

def generate_response(prompt_text):
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        contents = [
            types.Content(
                role="user",
                parts=[types.Part(text=prompt_text)],
            )
        ]
        config = types.GenerateContentConfig(response_mime_type="text/plain")
        response = client.models.generate_content_stream(model=model, contents=contents, config=config)
        
        # Cleanly join response
        return "".join(chunk.text for chunk in response).strip()
    except Exception as e:
        return f"❌ Error: {e}"

def on_hotkey():
    print("🟡 Hotkey pressed. Reading clipboard...")

    prompt_text = pyperclip.paste().strip()
    if not prompt_text:
        print("❗ Clipboard is empty.")
        return

    print(f"🔵 Prompt to Gemini: {prompt_text}")
    response_text = generate_response(prompt_text)

    print("🟢 Typing response at cursor...")
    pyperclip.copy(response_text)
    pyautogui.hotkey("ctrl", "v")  # Paste directly

def main():
    print("✅ Ready! Press Ctrl+Alt+Space to run AI.")
    keyboard.add_hotkey('ctrl+alt+space', lambda: threading.Thread(target=on_hotkey).start())
    keyboard.wait()

if __name__ == "__main__":
    main()
