from sarvam_streaming_stt import stream_audio_to_sarvam
from rag_pipeline import run_rag
from tts import speak, set_voice
import uuid


# ==========================================================
# USER SESSION (Generate at Runtime)
# ==========================================================

USER_ID = str(uuid.uuid4())
CUSTOMER_TYPE: str | None = None

print(f"🆔 Session ID: {USER_ID}")


# ==========================================================
# VOICE SELECTION
# ==========================================================


def choose_voice():
    print("\n🎤 Select Assistant Voice\n")

    print("1 → shubh (male)")
    print("2 → rohan (Male)")
    print("3 → priya (Female)")
    print("4 → Kavya (Female)")
    print("5 → shruti(Female)")

    choice = input("\nEnter voice number: ").strip()

    voice_map = {
        "1": "shubh",
        "2": "rohan",
        "3": "priya",
        "4": "Kavya",
        "5": "shruti",
    }

    selected_voice = voice_map.get(choice, "Aditya")

    set_voice(selected_voice)


# ==========================================================
# CUSTOMER TYPE SELECTION
# ==========================================================


def choose_customer_type():
    global CUSTOMER_TYPE

    print("\n📦 Select Customer Type\n")

    print("1 → ecommerce")
    print("2 → car_booking")

    choice = input("\nEnter choice: ").strip().lower()

    if choice in ["1", "ecommerce", "e"]:
        CUSTOMER_TYPE = "ecommerce"
    else:
        CUSTOMER_TYPE = "car_booking"

    print(f"\n✅ Using '{CUSTOMER_TYPE}' collection for this session.")


# ==========================================================
# HANDLE USER QUERY
# ==========================================================


def handle_query(text: str):
    print("\n🚀 Running RAG...\n")

    try:
        response = run_rag(USER_ID, text, customer_type=CUSTOMER_TYPE)

        print("\n🤖 Assistant Response:\n")
        print(response)

        print("\n========================\n")

        # Convert response to speech
        speak(response)

    except Exception as e:
        print("❌ Error during RAG execution:", str(e))


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":
    print("\n🎤 Voice RAG Session Started\n")

    choose_voice()

    choose_customer_type()

    print("\n🎧 Listening... Speak continuously (Ctrl+C to stop)\n")

    # Start streaming speech → STT → RAG → TTS
    stream_audio_to_sarvam(handle_query)
