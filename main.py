from Chatbot import Chatbot
from SpeechRecognizer import SpeechRecognizer
from TextToSpeech import TextToSpeech

import time
import random

from wakeupdetector import WakeUpDetector

FALLBACK_RESPONSES = ["Yes?", "I'm listening.", "How can I help you?"]

def speak_streaming_response(stream, tts):
    response = ""
    sentence_buffer = ""
    sentence_endings = {'.', '!', '?'}

    for chunk in stream:
        word = chunk["message"]["content"]
        print(word, end="", flush=True)
        response += word
        sentence_buffer += word

        if any(word.strip().endswith(p) for p in sentence_endings):
            sentence = sentence_buffer.strip()
            if sentence:
                tts.speak(sentence)
                sentence_buffer = ""

    if sentence_buffer.strip():
        tts.speak(sentence_buffer.strip())

    print()
    return response.strip()

def main():
    chatbot = Chatbot()
    tts = TextToSpeech()
    recognizer = SpeechRecognizer()
    detector = WakeUpDetector()

    print("🎤 Voice Assistant is running.")
    print("Press Enter to start recording your voice command, or type 'exit' to quit.")

    while True:
        detector.listen_for_wake_word()

        print("🎧 Listening for speech (silence-based)...")
        user_input = recognizer.listen()

        if not user_input.strip():
            response = random.choice(FALLBACK_RESPONSES)
            print(response)
            tts.speak(response)
            tts.stop_stream()
            continue

        print(f"Processing: {user_input}")
        result = chatbot.stream_response(user_input)

        if result["action"] == "chat":
            response = speak_streaming_response(result["stream"], tts)
            if "lights on" in response.lower():
                chatbot.call_api("lights_on_command")
            elif "lights off" in response.lower():
                chatbot.call_api("lights_off_command")

        elif result["action"] == "open_door":
            tts.speak("Please face the camera for recognition.")
            door_result = chatbot.call_api("open_door_command")
            time.sleep(1)
            if door_result.get("status") == "success":
                user = door_result.get("user", "unknown")
                tts.speak(f"Door opened for {user}.")
            else:
                tts.speak(f"Access denied: {door_result.get('message', 'Failed')}")

        elif result["action"] == "error":
            print(f"Error: {result['message']}")

        tts.stop_stream()
        print("\nVoice Assistant ready. Press Enter to record the next command or type 'exit' to quit.")

if __name__ == "__main__":
    main()
