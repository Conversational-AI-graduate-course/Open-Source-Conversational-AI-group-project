import requests

def transcribe_wav(file_path: str) -> str:
    """
    Transcribes a .wav file using the Rhasspy API and returns the result

    Args:
        file_path (str): Path to the .wav file to transcribe

    Returns:
        str: Transcription result
    """

    api_endpoint = 'http://localhost:12101/api/speech-to-text'

    try:
        recording = open(file_path, 'rb')
    except:
        raise FileNotFoundError("Error: Could not open file")
    
    headers = {'Content-Type': 'audio/wav'}

    response = requests.post(api_endpoint, recording, headers=headers)

    if response.status_code != 200:
        raise ConnectionError(f"Error: {response.status_code}")

    return response.text

def speak_text(text: str) -> None:
    """
    Speaks the provided text using the Rhasspy API

    Args:
        text (str): Text to speak
    """

    api_endpoint = 'http://localhost:12101/api/text-to-speech'

    response = requests.post(api_endpoint, data=text)

    if response.status_code != 200:
        raise ConnectionError(f"Error: {response.status_code}")
    
def text_intent(text: str) -> None:
    """
    Defines the Intent based on the provided text using th Rhasspy API

    Args:
        text (str):  Text to create intent from
    """

    api_endpoint = 'http://localhost:12101/api/text-to-intent'

    response = requests.post(api_endpoint, data=text)

    if response.status_code != 200:
        raise  ConnectionError(f"Error: {response.status_code}")
    
    if len(response.json().get("intent")['name']) > 1:
        return response.json().get("intent")['name']
    else:
        return "UnknownIntent"
    

