# ==========================================================
# 🔊 SARVAM TEXT TO SPEECH (SDK VERSION)
# Handles:
# ✅ Sarvam SDK response
# ✅ Base64 audio decoding
# ✅ Saves REAL playable WAV file
# ==========================================================

from sarvamai import SarvamAI
import base64
import os
from datetime import datetime
from config import SARVAM_API_KEY

# ==========================================================
# CONFIG
# ==========================================================

MODEL = "bulbul:v3"
CURRENT_VOICE = "priya"

client = SarvamAI(api_subscription_key=SARVAM_API_KEY)

AUDIO_DIR = "audio_outputs"
os.makedirs(AUDIO_DIR, exist_ok=True)


# ==========================================================
# VOICE SELECTION
# ==========================================================


def set_voice(voice_name: str):
    """
    Set the assistant voice
    """
    global CURRENT_VOICE

    CURRENT_VOICE = voice_name.lower()

    print(f"✅ Voice selected: {CURRENT_VOICE}")


# ==========================================================
# GENERATE FILE NAME
# ==========================================================


def generate_filename():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(AUDIO_DIR, f"response_{timestamp}.wav")


# ==========================================================
# TEXT → SPEECH
# ==========================================================


def speak(text: str):
    try:
        response = client.text_to_speech.convert(
            text=text, target_language_code="en-IN", model=MODEL, speaker=CURRENT_VOICE
        )

        # Extract base64 audio
        audio_base64 = response.audios[0]

        # Decode audio
        audio_bytes = base64.b64decode(audio_base64)

        filepath = generate_filename()

        # Save file
        with open(filepath, "wb") as f:
            f.write(audio_bytes)

        print(f"💾 Audio saved successfully:\n{filepath}")

        return filepath

    except Exception as e:
        print("❌ TTS Error:", str(e))
        return None
