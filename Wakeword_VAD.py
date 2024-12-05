import pyaudio
import numpy as np
from openwakeword.model import Model
import argparse
import threading
import numpy as np
import torch
torch.set_num_threads(1)
import pyaudio
import time
import os
import wave
import openwakeword

openwakeword.utils.download_models()

# Parse input arguments
parser=argparse.ArgumentParser()
parser.add_argument(
    "--chunk_size",
    help="How much audio (in number of samples) to predict on at once",
    type=int,
    default=800,
    required=False
)
parser.add_argument(
    "--model_path",
    help="The path of a specific model to load",
    type=str,
    default="",
    required=False
)
parser.add_argument(
    "--inference_framework",
    help="The inference framework to use (either 'onnx' or 'tflite'",
    type=str,
    default='tflite',
    required=False
)

args=parser.parse_args()

# Get microphone stream
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = args.chunk_size
audio = pyaudio.PyAudio()
mic_stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

# Load pre-trained openwakeword models
if args.model_path != "":
    owwModel = Model(wakeword_models=[args.model_path], inference_framework=args.inference_framework)
else:
    owwModel = Model(inference_framework=args.inference_framework)

n_models = len(owwModel.models.keys())



SILENCE_THRESHOLD = 0.5 
SILENCE_DURATION = 2.0  #s

FORMAT = pyaudio.paInt16
CHANNELS = 1
SAMPLE_RATE = 16000

NUM_SAMPLES = 512

continue_recording = True
silence_detected = False  

folder_name = "recordings"
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

# Generate a unique file name with a timestamp
timestamp = time.strftime("%Y%m%d-%H%M%S")  # Format: YYYYMMDD-HHMMSS
filename = os.path.join(folder_name, f"output_{timestamp}.wav")


model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                              model='silero_vad',
                              force_reload=True)
(get_speech_timestamps,
 save_audio,
 read_audio,
 VADIterator,
 collect_chunks) = utils
continue_recording = True

# Provided by Alexander Veysov
def int2float(sound):
    abs_max = np.abs(sound).max()
    sound = sound.astype('float32')
    if abs_max > 0:
        sound *= 1/32768
    sound = sound.squeeze()  # depends on the use case
    return sound


def stop():
    
    global continue_recording
    global silence_detected
    while continue_recording and not silence_detected:
        time.sleep(0.1)  # avoid busy waiting
    continue_recording = False  
    
def start_listening():

    # Generate output string header
    print("\n\n")
    print("#"*100)
    print("Listening for wakewords...")
    print("#"*100)
    print("\n"*(n_models*3))

    # WAKEWORD DETECTION
    wakeword_detected = False
    while wakeword_detected==False:
        
        audio_chunk = mic_stream.read(CHUNK)
        
        audio_sign = np.frombuffer(audio_chunk, dtype=np.int16)

        prediction = owwModel.predict(audio_sign)

        for mdl in owwModel.prediction_buffer.keys():
            
            scores = list(owwModel.prediction_buffer[mdl])
            curr_score = format(scores[-1], '.20f').replace("-", "")
            if float(curr_score) >= 0.5: 
                wakeword_detected = True
                print("Wakeword detected")
                
                    
    print("\n\n")
    print("#"*100)
    print("Recording...")
    print("#"*100)
    voiced_confidences = []
    silence_start = None  # Track when silence starts
    frames = []
    buffer = np.array([], dtype=np.int16)

    global continue_recording
    global silence_detected
    continue_recording = True
    silence_detected = False

    stop_listener = threading.Thread(target=stop)
    stop_listener.start()

    while continue_recording:
        audio_chunk = mic_stream.read(CHUNK)
        audio_sign = np.frombuffer(audio_chunk, dtype=np.int16)
        
        # In case you want to save the audio later
        frames.append(audio_chunk)

        # Buffering required to fix numsample and chunk mismatch of different models
        audio_int16 = np.frombuffer(audio_chunk, np.int16)
        buffer = np.concatenate((buffer, audio_int16))
        audio_int16 = buffer[:NUM_SAMPLES]
        buffer = buffer[NUM_SAMPLES:]

        audio_float32 = int2float(audio_int16)
              
        # Get the confidences and add them to the list to plot them later
        new_confidence = model(torch.from_numpy(audio_float32), SAMPLE_RATE).item()
        voiced_confidences.append(new_confidence)

        # Check for silence
        if new_confidence < SILENCE_THRESHOLD:
            if silence_start is None:
                silence_start = time.time()  # Silence start
            elif time.time() - silence_start >= SILENCE_DURATION:
                print("Detected 2 seconds of silence. Stopping recording.")
                silence_detected = True  
                stop_listener.join()
                # Stop and close the stream
                
                mic_stream.stop_stream()
                mic_stream.close()
                audio.terminate()
                return frames
                
        else:
            silence_start = None  # Reset silence timer if voice activity is detected


# Run capture loop continuosly, checking for wakewords
if __name__ == "__main__":
    frames = start_listening()
    # Save the recorded audio as a WAV file
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)  # Stereo
        wf.setsampwidth(2)  # Explicitly set to 2 bytes (16-bit depth)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframesraw(b''.join(frames))

    print(f"Audio saved as {filename}")