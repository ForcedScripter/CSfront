# ==========================================================
# 🔊 TEXT → WAV (SARVAM TTS)
# Converts API audio (bytes/base64) → Proper WAV file
# ==========================================================

import requests
import base64
import wave
import os
from datetime import datetime

# ==========================================================
# CONFIG
# ==========================================================

SARVAM_API_KEY = "sk_s9c7y8bc_e1KNE0e5gEKmWYxCbx5BZTLk"
TTS_URL = "https://api.sarvam.ai/text-to-speech"

MODEL = "bulbul:v3"
VOICE = "Kavya"

OUTPUT_DIR = "audio_outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ==========================================================
# GENERATE FILE NAME
# ==========================================================


def generate_filename():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(OUTPUT_DIR, f"tts_{timestamp}.wav")


# ==========================================================
# SAVE RAW PCM → WAV
# ==========================================================


def save_pcm_as_wav(
    audio_bytes, filename, channels=1, sample_width=2, sample_rate=22050
):
    """
    channels = 1 (mono)
    sample_width = 2 (16-bit audio)
    sample_rate = 22050 or 24000 (Sarvam default)
    """

    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_bytes)

    print("✅ WAV file saved:", filename)


# ==========================================================
# MAIN FUNCTION
# ==========================================================


def text_to_wav(text):
    headers = {
        "Authorization": f"Bearer {SARVAM_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {"model": MODEL, "voice": VOICE, "text": text}

    response = requests.post(TTS_URL, headers=headers, json=payload)

    if response.status_code != 200:
        print("❌ Error:", response.text)
        return

    content_type = response.headers.get("Content-Type", "")

    # ======================================================
    # CASE 1: DIRECT AUDIO RESPONSE
    # ======================================================
    if "audio" in content_type:
        audio_bytes = response.content

    # ======================================================
    # CASE 2: JSON WITH BASE64 AUDIO
    # ======================================================
    else:
        data = response.json()
        audio_base64 = data["audios"][0]
        audio_bytes = base64.b64decode(audio_base64)

    # ======================================================
    # SAVE AS WAV
    # ======================================================
    filename = generate_filename()
    save_pcm_as_wav(audio_bytes, filename)


# ==========================================================
# RUN
# ==========================================================

if __name__ == "__main__":
    user_text = input("Enter text to convert to audio:\n>> ")
    text_to_wav(user_text)
