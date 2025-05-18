import pyaudio
import numpy as np
import torch
from transformers import FastSpeech2ConformerTokenizer, FastSpeech2ConformerWithHifiGan
from threading import Thread
from queue import Queue
import time
from torch.cuda.amp import autocast

class TextToSpeech:
    def __init__(self):
        print("🔄 Initializing FastSpeech2ConformerWithHifiGan...")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"🔹 Using device: {self.device}")
        self.tokenizer = FastSpeech2ConformerTokenizer.from_pretrained("espnet/fastspeech2_conformer")
        self.model = FastSpeech2ConformerWithHifiGan.from_pretrained("espnet/fastspeech2_conformer_with_hifigan")
        self.model = self.model.to(self.device)
        self.model.eval()
        print("✅ TTS Model Initialized. Note: Some vocoder weights are newly initialized and may require fine-tuning for optimal quality.")
        
        # Initialize PyAudio
        self.p = pyaudio.PyAudio()
        self.sample_rate = 22050
        self.stream = self.p.open(format=pyaudio.paFloat32,
                                 channels=1,
                                 rate=self.sample_rate,
                                 output=True,
                                 frames_per_buffer=1024)
        self.audio_queue = Queue()

    def stream_audio(self):
        """Play audio from the queue."""
        while True:
            waveform = self.audio_queue.get()
            if waveform is None:  # Sentinel to stop
                break
            self.stream.write(waveform.tobytes())
            self.audio_queue.task_done()

    def synthesize_chunk(self, text_chunk):
        """Generate waveform for a single text chunk with mixed precision."""
        start_time = time.time()
        inputs = self.tokenizer(text_chunk, return_tensors="pt").to(self.device)
        input_ids = inputs["input_ids"]
        try:
            with torch.no_grad(), autocast():
                output_dict = self.model(input_ids, return_dict=True)
                waveform = output_dict["waveform"].squeeze().detach().cpu().numpy()
        except Exception as e:
            print(f"❌ Synthesis error for chunk '{text_chunk}': {e}")
            return None
        
        # Normalize waveform
        waveform = waveform.astype(np.float32)
        if waveform.max() > 1.0 or waveform.min() < -1.0:
            waveform = waveform / np.max(np.abs(waveform))
        
        print(f"Chunk '{text_chunk}' synthesized in {time.time() - start_time:.3f}s")
        return waveform

    def speak(self, text):
        """Synthesize and stream a single sentence."""
        if not text.strip():
            return
        
        # Start streaming thread if not already running
        if not hasattr(self, 'stream_thread') or not self.stream_thread.is_alive():
            self.stream_thread = Thread(target=self.stream_audio)
            self.stream_thread.start()

        # Synthesize and queue waveform
        try:
            waveform = self.synthesize_chunk(text)
            if waveform is not None:
                self.audio_queue.put(waveform)
        except Exception as e:
            print(f"❌ Error during synthesis: {e}")

    def stop_stream(self):
        """Stop the streaming thread."""
        if hasattr(self, 'stream_thread') and self.stream_thread.is_alive():
            self.audio_queue.put(None)  # Signal streaming thread to stop
            self.stream_thread.join()

    def __del__(self):
        """Clean up PyAudio resources."""
        try:
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()
        except:
            pass