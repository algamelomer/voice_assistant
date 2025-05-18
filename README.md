# Voice Assistant

Voice Assistant is an intelligent, voice-activated smart home companion designed to simplify your life. Control your home devices, access real-time environmental data, and interact naturally using voice commands. Whether you want to turn on the lights, unlock the door with face recognition, or check the temperature, Voice Assistant has you covered—all triggered by a customizable wake word like "Jarvis."

## Features

- **Wake Word Activation**: Listens for a wake word (e.g., "Jarvis") to spring into action.
- **Speech Recognition**: Converts your voice commands into text with high accuracy.
- **Natural Language Understanding**: Processes commands and queries using a powerful chatbot.
- **Voice Responses**: Replies with clear, natural-sounding speech.
- **Smart Home Control**: Manages lights, fans, and doors via API integrations.
- **Environmental Insights**: Provides temperature, humidity, and full environment status updates.
- **Secure Door Access**: Opens doors after verifying your identity with face recognition.

## Technologies Used

- **Ollama (Mistral)**: Drives the chatbot for natural language processing.
- **FasterWhisper**: Delivers fast and precise speech-to-text conversion.
- **FastSpeech2ConformerWithHifiGan**: Generates natural voice responses.
- **PyAudio**: Handles audio input and output seamlessly.
- **Porcupine**: Detects the wake word to activate the assistant.
- **Smart Home APIs**: Connects to devices for real-time control.

## Installation

### Prerequisites

- **Python 3.x**: Ensure you have a compatible version installed.
- **Porcupine Access Key**: Required for wake word detection (sign up at [Picovoice](https://picovoice.ai/) to get one).
- **Smart Home API Access**: Configure your device APIs (e.g., lights, doors) for integration.

### Setting Up the Environment

1. **Clone the Repository**:
   ```sh
   git clone https://github.com/yourusername/voice_assistant.git
   cd voice_assistant
   ```

2. **Create a Virtual Environment**:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```sh
   pip install -r requirements.txt
   ```
   *Note*: Ensure you have all packages listed, including `ollama`, `faster_whisper`, `pyaudio`, `pvporcupine`, and others.

4. **Configure Porcupine**:
   - Open `wakeupdetector.py` and replace the `access_key` with your Porcupine access key:
     ```python
     access_key = "YOUR_ACCESS_KEY_HERE"
     ```

5. **Set Up Configuration**:
   - Edit `config.json` to include your API endpoints and customize prompts:
     - Update `api_endpoints` with your smart home device URLs.
     - Adjust prompts (e.g., `general_prompt`, `open_door_command`) as needed.

## Usage

1. **Launch the Assistant**:
   ```sh
   python main.py
   ```

2. **Activate with Wake Word**:
   - Say "Jarvis" (or your configured wake word) to wake up the assistant.

3. **Issue Commands**:
   - "Turn on the lights" → Controls the lights.
   - "Open the door" → Triggers face recognition and opens the door if verified.
   - "What’s the temperature?" → Provides the current temperature.

4. **Listen for Responses**:
   - The assistant will reply with a voice response and perform the requested action.

5. **Stop the Assistant**:
   - Interrupt the process (e.g., Ctrl+C) to exit.

### Example Commands
- "Turn off the fan"
- "Check the humidity"
- "Close the door"

## Contributing

We’d love your help to make Voice Assistant even better! To contribute:

1. Fork the repository.
2. Create a branch for your feature or fix (`git checkout -b feature-name`).
3. Commit your changes (`git commit -m "Add feature"`).
4. Push to your fork (`git push origin feature-name`).
5. Open a pull request with a clear description of your updates.

*Ideas for contributions*:
- Enhance wake word detection accuracy.
- Fine-tune the text-to-speech model for better voice quality.
- Add support for more smart home devices.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

**Note**: The text-to-speech output may sound robotic initially. Fine-tuning the `FastSpeech2ConformerWithHifiGan` model is recommended for optimal quality—join us in improving it!
