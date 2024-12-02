from src.api import transcribe_wav, speak_text  # Get functions from api.py
import subprocess
import json

# Main function that has a tentative workflow
def main():
    # Step 1: Get the transcription of the audio file
    audio_file = "./recordings/weather.wav"  # Path to the audio file
    transcription = transcribe_wav(audio_file)  # Transcribe the audio
    print("Step 1:The transcription is:", transcription)  # Show the transcription
    
    # Step 2: Match the transcription to an intent (To be defined)
    # This dictionary should be updated with the sentences.ini file
    intents_map = {
        "create file": "CreateFile",
        "what time is it": "GetTime",
        "tell me the time": "GetTime",
    }
    # Find the intent for the transcription
    intent = intents_map.get(transcription.lower(), "UnknownIntent")
    print("Step 2: The intent:", intent)

    if intent == "UnknownIntent": 
        print("Sorry, I didn't understand that.") 
        return  # Stop the program

    # Step 3: Run command.py to handle the intent
    response = run_command(intent, transcription) 
    print("Step 3 The response is:", response) 
    
    # Step 4: Speak the response using text-to-speech
    speak_text(response)  # Convert the response text to speech

# Function to run the command.py script
def run_command(intent, transcription):
    # That command.py expects a JSON input 
    command_input = {
        "intent": {"name": intent},  # The intent name (GetTime)
        "text": transcription        # The transcription text
    }

    # Use subprocess to run command.py
    process = subprocess.Popen(
        ["python", "src/command.py"],  # Command to run command.py
        stdin=subprocess.PIPE,         # Send input to the script
        stdout=subprocess.PIPE         # Capture the script's output
    )
    
    # Send the JSON data to command.py and get its output
    stdout, _ = process.communicate(input=json.dumps(command_input).encode())
    
    # Parse the output JSON and return the response text
    return json.loads(stdout)["speech"]["text"]


# Run the main function when the script starts
if __name__ == "__main__":
    main()