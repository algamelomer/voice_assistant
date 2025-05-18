import json
import ollama
import requests
import time

class Chatbot:
    def __init__(self, config_path="config.json"):
        print("🔄 Initializing Chatbot...")
        self.model_name = "mistral"

        try:
            with open(config_path, "r") as f:
                config_data = json.load(f)

            self.general_prompt = config_data.get("general_prompt", "")
            self.doctor_prompt = config_data.get("doctor_prompt", "")
            self.job_prompt = config_data.get("job_prompt", "")
            self.smart_city_prompt = config_data.get("smart_city_prompt", "")
            self.api_instructions = config_data.get("api_instructions", "")

            self.verified_user = False 
            self.isdooropened = False
            self.isfanon = False
            self.islightson = False

            self.open_door_command = config_data.get("open_door_command", "")
            self.lights_on_command = config_data.get("lights_on_command", "")
            self.lights_off_command = config_data.get("lights_off_command", "")

            self.close_door_command = config_data.get("close_door_command", "")
            self.fan_on_command = config_data.get("fan_on_command", "")
            self.fan_off_command = config_data.get("fan_off_command", "")
            self.environment = config_data.get("environment", "")
            self.wheater = config_data.get("wheater", "")
            self.temperature = config_data.get("temperature", "")
            self.humidity = config_data.get("humidity", "")

            self.api_endpoints = config_data.get("api_endpoints", {})
            self.door_open_api = config_data.get("door_open_api", "")

            print("✅ Configuration loaded successfully!")
        except Exception as e:
            print(f"❌ Error loading configuration: {e}")
            self.general_prompt = ""
            self.doctor_prompt = ""
            self.job_prompt = ""
            self.smart_city_prompt = ""
            self.open_door_command = ""
            self.api_instructions = ""
            self.lights_on_command = ""
            self.lights_off_command = ""

            self.close_door_command = ""
            self.fan_on_command = ""
            self.fan_off_command = ""
            self.environment = ""
            self.wheater = ""
            self.temperature = ""
            self.humidity = ""

            self.api_endpoints = {}

        print(f"🤖 Using Ollama model: {self.model_name}")

    def get_full_system_prompt(self):
        parts = [
            self.general_prompt,
            self.doctor_prompt,
            self.job_prompt,
            self.smart_city_prompt,
            self.api_instructions,
            self.lights_on_command,
            self.lights_off_command,
            self.open_door_command
        ]
        return "\n".join(part for part in parts if part)

    def call_api(self, endpoint, method="POST"):
        endpoint_config = self.api_endpoints.get(endpoint)
        if not endpoint_config:
            print(f"❌ Endpoint '{endpoint}' not configured")
            return {"status": "error", "message": "Endpoint not configured"}

        url = endpoint_config.get("url")
        method = endpoint_config.get("method", method).upper()

        try:
            response = requests.request(method, url)
            if response.status_code == 200:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    return {"status": "success"}
            return {"status": "error", "message": f"API returned {response.status_code}"}
        except Exception as e:
            print(f"🔴 API Error: {e}")
            return {"status": "error", "message": str(e)}

    def _handle_sensor_data(self, endpoint, data_key, unit):
        """Helper method to handle sensor data responses"""
        data = self.call_api(endpoint, method="GET")
        try:
            value = data.get('data', {}).get(data_key, 'unknown')
            message = f"Current {data_key}: {value}{unit}"
            return message, True, [message]
        except (AttributeError, KeyError):
            return "Could not read sensor data", True, ["Could not read sensor data"]

    def _handle_environment_data(self):
        """Helper method to handle full environment data"""
        env_data = self.call_api("get_environment", method="GET")
        try:
            temp = env_data.get('data', {}).get('temperature', 'unknown')
            humidity = env_data.get('data', {}).get('humidity', 'unknown')
            message = f"Environment: {temp}°C, {humidity}% humidity"
            return message, True, [message]
        except (AttributeError, KeyError):
            return "Could not read environment data", True, ["Could not read environment data"]
        
    def stream_response(self, user_input):
        # Pre-processing
        if "morsi" in user_input.lower():
            user_input = user_input.replace("morsi", "smart city")

        full_system_prompt = self.get_full_system_prompt()
        messages = [
            {"role": "system", "content": full_system_prompt},
            {"role": "user", "content": user_input}
        ]

        try:
            # Create a generator to process the stream and handle commands
            def process_stream():
                response = ""
                sentences = []
                sentence_buffer = ""
                sentence_endings = {'.', '!', '?'}

                for chunk in ollama.chat(
                    model=self.model_name,
                    messages=messages,
                    options={"max_tokens": 50},
                    stream=True,
                ):
                    word = chunk["message"]["content"]
                    response += word
                    sentence_buffer += word

                    if any(word.strip().endswith(p) for p in sentence_endings):
                        sentence = sentence_buffer.strip()
                        if sentence:
                            sentences.append(sentence)
                            sentence_buffer = ""

                    # Yield the chunk for streaming
                    yield chunk

                    # Check for face recognition
                    if "initiate face recognition for access" in response.lower():
                        print("🔍 Running face recognition...")
                        result = self.call_api("open_door_command")

                        if result.get("status") == "success":
                            user = result.get("user", "unknown")
                            self.verified_user = True
                            print("✅ Face verified. Opening door...")

                            if self.door_open_api:
                                try:
                                    door_response = requests.post(self.door_open_api)
                                    print(f"🚪 Door open response: {door_response.text}")
                                except Exception as e:
                                    print(f"❌ Failed to open door: {e}")

                            # Yield a custom chunk to indicate door open
                            yield {
                                "message": {
                                    "content": f"Door opened for {user}."
                                }
                            }
                            return
                        else:
                            self.verified_user = False
                            message = result.get("message", "Face recognition failed")
                            yield {
                                "message": {
                                    "content": f"Access denied: {message}"
                                }
                            }
                            return

                if sentence_buffer.strip():
                    sentences.append(sentence_buffer.strip())

                # After streaming, handle other commands if verified
                if self.verified_user:
                    clean_response = response.replace('\\', '').lower().strip()
                    
                    if "lights_on_command" in clean_response:
                        self.call_api("lights_on_command")
                        yield {
                            "message": {
                                "content": "Turning on the lights..."
                            }
                        }
                        return
                    elif "lights_off_command" in clean_response:
                        self.call_api("lights_off_command")
                        yield {
                            "message": {
                                "content": "Turning off the lights..."
                            }
                        }
                        return
                    elif "fan_on_command" in clean_response:
                        self.call_api("fan_on_command")
                        yield {
                            "message": {
                                "content": "Turning on the fan..."
                            }
                        }
                        return
                    elif "fan_off_command" in clean_response:
                        self.call_api("fan_off_command")
                        yield {
                            "message": {
                                "content": "Turning off the fan..."
                            }
                        }
                        return
                    elif "humidity" in clean_response:
                        message, _, _ = self._handle_sensor_data("get_humidity", "humidity", "%")
                        yield {
                            "message": {
                                "content": message
                            }
                        }
                        return
                    elif "weather" in clean_response or "temperature" in clean_response:
                        message, _, _ = self._handle_sensor_data("get_temperature", "temperature", "°C")
                        yield {
                            "message": {
                                "content": message
                            }
                        }
                        return
                    elif "environment" in clean_response:
                        message, _, _ = self._handle_environment_data()
                        yield {
                            "message": {
                                "content": message
                            }
                        }
                        return
                    elif "close_door_command" in clean_response:
                        self.call_api("close_door_command")
                        yield {
                            "message": {
                                "content": "Closing the door..."
                            }
                        }
                        return

            return {
                "action": "chat",
                "stream": process_stream()
            }
        except Exception as e:
            print(f"❌ Error during streaming response: {e}")
            return {"action": "error", "message": str(e)}
