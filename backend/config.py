from dotenv import load_dotenv
import os

load_dotenv()  # load .env file

YOUR_GEMINI_KEY = os.getenv("YOUR_GEMINI_KEY")

if not YOUR_GEMINI_KEY:
    raise RuntimeError("Missing YOUR_GEMINI_KEY in .env file")
