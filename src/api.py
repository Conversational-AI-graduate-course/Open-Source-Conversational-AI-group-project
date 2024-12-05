import requests

def transcribe_wav(file_path: str) -> str:
    """
    Transcribes a .wav file using the Rhasspy API and returns the result

    Args:
        file_path (str): Path to the .wav file to transcribe

    Returns:
        str: Transcription result
    """

    try:
        with open('src/resources/sentences.ini', 'r') as sentences_file:
            sentences = sentences_file.read()
            api_endpoint_sentences = 'http://localhost:12101/api/sentences'
            response_sentences = requests.post(api_endpoint_sentences, sentences)
            if response_sentences.status_code != 200:
                raise ConnectionError(f"Error: {response_sentences.status_code}")
    except FileNotFoundError:
        raise FileNotFoundError("Error: Could not open sentences.ini file")

    try:
        with open(file_path, 'rb') as recording:
            api_endpoint = 'http://localhost:12101/api/speech-to-text'
            response = requests.post(api_endpoint, recording, headers={'Content-Type': 'audio/wav'})
            if response.status_code != 200:
                raise ConnectionError(f"Error: {response.status_code}")
    except FileNotFoundError:
        raise FileNotFoundError("Error: Could not open file")

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
