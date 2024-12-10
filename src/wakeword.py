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
import wave
import os 

# Parse input arguments
parser=argparse.ArgumentParser()

parser.add_argument(
    "--wake_word",
    help="The path of a specific model to load",
    type=str,
    default="Yoh Dewd",
    required=False
)

args=parser.parse_args()

# Get microphone stream
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 800
audio = pyaudio.PyAudio()
mic_stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

# Wakeword model
model_path = f"wakeword_model/{args.wake_word.replace(' ', '_')}.tflite"
if not os.path.exists(model_path):
    raise FileNotFoundError(f"The specified model path does not exist: {model_path}")
inference_framework = "tflite"

owwModel = Model(wakeword_models=[model_path], inference_framework=inference_framework)

# VAD and silence parameters
SILENCE_THRESHOLD = 0.5 
SILENCE_DURATION = 2.0  #s

NUM_SAMPLES = 512

continue_recording = True
silence_detected = False  


model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                              model='silero_vad',
                              force_reload=True)
(get_speech_timestamps,
 save_audio,
 read_audio,
 VADIterator,
 collect_chunks) = utils

# Provided by Alexander Veysov
def int2float(sound):
    abs_max = np.abs(sound).max()
    sound = sound.astype('float32')
    if abs_max > 0:
        sound *= 1/32768
    sound = sound.squeeze()  # depends on the use case
    return sound

# stop if silence detected
def stop():
    global continue_recording
    global silence_detected
    while continue_recording and not silence_detected:
        time.sleep(0.1)  # avoid busy waiting
    continue_recording = False  
    
def start_listening():
    global continue_recording
    global silence_detected

    # Generate output string header
    print("\n\n")
    print("#"*100)
    print("Listening for wakewords...")
    print("#"*100)
    print("\n"*(3))

    # WAKEWORD DETECTION
    wakeword_detected = False
    while not wakeword_detected:
        
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
        new_confidence = model(torch.from_numpy(audio_float32), RATE).item()
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

def save_frames_to_wav(frames, filename):
    
    # Save the recorded audio as a WAV file
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)  # Stereo
        wf.setsampwidth(2)  # Explicitly set to 2 bytes (16-bit depth)
        wf.setframerate(RATE)
        wf.writeframesraw(b''.join(frames))

    print(f"Audio saved as {filename}")
