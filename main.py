from src.api import transcribe_wav, speak_text  # Get functions from api.py
import subprocess
import json

def run_command(intent, transcription):
    """
    Run the command.py script with the intent and transcription.
    """
    # Create the JSON object for input
    command_input = {
        "intent": {"name": intent},
        "text": transcription
    }

    # Run command.py using subprocess
    process = subprocess.Popen(
        ["python", "src/command.py"],  # Command to run
        stdin=subprocess.PIPE,         # Send input through stdin
        stdout=subprocess.PIPE         # Capture output
    )
    
    # Send the JSON input and capture the output
    stdout, _ = process.communicate(input=json.dumps(command_input).encode())
    return json.loads(stdout)["speech"]["text"]  # Extract the response

def main():
    # Step 1: Transcribe the audio
    audio_file = "./recordings/lamp.wav"
    transcription = transcribe_wav(audio_file)
    print("Transcription:", transcription)
    
    # Step 2: Map the transcription to an intent
    intents_map = {
        "create file": "CreateFile",
        "what time is it": "GetTime",
        "tell me the time": "GetTime",
        "whats the temperature": "GetTemperature",
        "how hot is it": "GetTemperature",
        "how cold is it": "GetTemperature",
    }
    intent = intents_map.get(transcription.lower(), "UnknownIntent")
    if intent == "UnknownIntent":
        print("Sorry, I didn't understand that.")
        return

    # Step 3: Run command.py and get the result
    response = run_command(intent, transcription)
    print("Response:", response)
    
    # Step 4: Speak the response
    speak_text(response)

if __name__ == "__main__":
    main()
