from src.api import transcribe_wav, speak_text, text_intent  
import subprocess
import json
import os
import time
import src.wakeword as wakeword
import configparser



# Main function with a tentative workflow
def main():
    folder_name = "recordings"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # Generate a unique file name with a timestamp
    timestamp = time.strftime("%Y%m%d-%H%M%S")  # Format: YYYYMMDD-HHMMSS
    filename = os.path.join(folder_name, f"output_{timestamp}.wav")

    frames = wakeword.start_listening()

    wakeword.save_frames_to_wav(frames, filename)


    # Step 1: Get the transcription of the audio file
    transcription = transcribe_wav(os.path.join(folder_name, filename))  # Transcribe the audio

    print("Step 1: Your transcription is:", transcription)  # Show the transcription
    
    # Step 2: Match the transcription to an intent
    intent = text_intent(transcription.lower())
    print("Step 2: Your intent is:", intent)

    if intent == "UnknownIntent": 
        print("Sorry, I didn't understand that.") 
        return  # Stop the program

    # Step 3: Run command.py to handle the intent
    response = run_command(intent, transcription) 
    print("Step 3: The response is:", response) 
    
    # Step 4: Speak the response using text-to-speech
    speak_text(response)  # Convert the response text to speech

# Function to run the command.py script. we need to rebuild this function!
def run_command(intent, transcription):
    """
    Sends the intent and transcription to command.py and gets the response.
    """
    # Prepare input as a JSON object
    input_data = {
        "intent": {"name": intent},
        "text": transcription
    }
    
    # Call command.py and send the input
    # `stdin` is for sending input, `stdout` is for receiving output
    process = subprocess.Popen(
        ["python", "src/command.py"],  # Run the command.py script
        stdin=subprocess.PIPE,         # Send input through stdin
        stdout=subprocess.PIPE         # Get output from stdout
    )
    
    # Send JSON input to command.py and receive its response
    stdout, _ = process.communicate(input=json.dumps(input_data).encode())
    
    # Convert the JSON response back into a dictionary
    output_data = json.loads(stdout)
    
    # Return the "speech" text from the response
    return output_data["speech"]["text"]

# Run the main function when the script starts
if __name__ == "__main__":
    main()
