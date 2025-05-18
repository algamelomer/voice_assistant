import numpy as np
import sounddevice as sd
import noisereduce as nr
import torch
from faster_whisper import WhisperModel

SAMPLE_RATE = 16000
SILENCE_THRESHOLD = 0.01 
SILENCE_DURATION = 2.5 

class SpeechRecognizer:
    def __init__(self):
        print("🔄 Loading FasterWhisper model for speech recognition...")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🖥️ Using device: {device}")
        self.model = WhisperModel("large-v2", device=device, compute_type="int8")
        self.listening = True

    def record_audio(self):
        if not self.listening:
            return None

        print("🎤 Listening... Speak now.")
        buffer = []
        silence_counter = 0
        chunk_duration = 0.1  # seconds
        chunk_size = int(SAMPLE_RATE * chunk_duration)

        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="float32") as stream:
            while True:
                chunk, _ = stream.read(chunk_size)
                chunk = chunk.flatten()
                # Apply noise reduction (optional)
                chunk = nr.reduce_noise(y=chunk, sr=SAMPLE_RATE, prop_decrease=0.5)
                
                volume = np.sqrt(np.mean(chunk**2))
                # print(f"DEBUG Volume: {volume:.5f}")  # Uncomment for debugging volume
                
                if volume < SILENCE_THRESHOLD:
                    silence_counter += 1
                    if silence_counter > (SILENCE_DURATION / chunk_duration):
                        print(f"🛑 Silence detected for {SILENCE_DURATION}s, stopping recording.")
                        break
                else:
                    silence_counter = 0
                    buffer.append(chunk)

        if buffer:
            audio = np.concatenate(buffer)
            return audio
        else:
            print("⚠️ No speech detected.")
            return None

    def transcribe_audio(self, audio):
        if audio is None or len(audio) == 0:
            return ""
        try:
            # Note: FasterWhisper can take raw numpy audio arrays directly
            segments, _ = self.model.transcribe(audio, beam_size=5, language="en")
            transcription = " ".join(segment.text for segment in segments).strip()
            return transcription
        except Exception as e:
            print(f"❌ Error during transcription: {e}")
            return ""

    def listen(self):
        """Convenience method to record and transcribe in one go."""
        audio = self.record_audio()
        return self.transcribe_audio(audio)

if __name__ == "__main__":
    recognizer = SpeechRecognizer()
    print("Press Enter to start recording your voice command, or type 'exit' to quit.")
    while True:
        user_input = input("> ").strip()
        if user_input.lower() in ["exit", "stop"]:
            print("👋 Exiting speech recognizer...")
            break
        print("🎧 Listening for speech...")
        transcription = recognizer.listen()
        if transcription:
            print(f"🗣️ You said: {transcription}")
        else:
            print("⚠️ No valid transcription.")