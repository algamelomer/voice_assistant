import pvporcupine
import pyaudio
import struct
import soundfile as sf
import sounddevice as sd
import os

class WakeUpDetector:
    def __init__(self, access_key="5abkCsFEmEzO2u1hUzsPUKZO8prJg4SS8wiLW/fWdtGN+Gr/Kpfcyg==", keywords=["jarvis"]):
        self.porcupine = pvporcupine.create(access_key=access_key, keywords=keywords)
        self.pa = pyaudio.PyAudio()
        self.audio_stream = self.pa.open(
            rate=self.porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.porcupine.frame_length)
        self.sound_path = os.path.join("sounds", "yes.wav")

    def play_wav(self, file_path):
        data, fs = sf.read(file_path, dtype='float32')  # load audio file as float32
        sd.play(data, fs)  # play audio
        sd.wait()  # wait until done playing

    def listen_for_wake_word(self):
        print("Listening for wake word...")
        try:
            while True:
                pcm = self.audio_stream.read(self.porcupine.frame_length, exception_on_overflow=False)
                pcm_unpacked = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
                result = self.porcupine.process(pcm_unpacked)
                if result >= 0:
                    print("Wake word detected!")
                    self.play_wav(self.sound_path)
                    break  # exit loop to start listening for commands
        except KeyboardInterrupt:
            print("Stopping wake word detector...")

    def cleanup(self):
        self.audio_stream.stop_stream()
        self.audio_stream.close()
        self.pa.terminate()
        self.porcupine.delete()

    def cleanup(self):
        self.audio_stream.stop_stream()
if __name__ == "__main__":
    detector = WakeUpDetector()
    try:
        while True:
            detector.listen_for_wake_word()
            # Here you can add code to listen for commands after wake word
            # For example, simulate command listening with input() or a placeholder
            print("Listening for commands... (simulate with input, press Enter to re-arm wake word detector)")
            input()
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        detector.cleanup()

# if __name__ == "__main__":
#     detector = WakeUpDetector()
#     detector.listen_for_wake_word()
