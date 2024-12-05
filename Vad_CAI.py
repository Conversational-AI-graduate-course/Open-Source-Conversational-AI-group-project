import threading
import numpy as np
import torch
torch.set_num_threads(1)
import pyaudio
import time
import os
import wave

SILENCE_THRESHOLD = 0.5 
SILENCE_DURATION = 2.0  #s

FORMAT = pyaudio.paInt16
CHANNELS = 1
SAMPLE_RATE = 8000
CHUNK = int(SAMPLE_RATE / 10)
NUM_SAMPLES = 256

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


audio = pyaudio.PyAudio()

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
    


def start_recording():
    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=SAMPLE_RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

    voiced_confidences = []
    silence_start = None  # Track when silence starts
    frames = []

    global continue_recording
    global silence_detected
    continue_recording = True
    silence_detected = False

    stop_listener = threading.Thread(target=stop)
    stop_listener.start()

    while continue_recording:
        audio_chunk = stream.read(NUM_SAMPLES)

        # In case you want to save the audio later
        frames.append(audio_chunk)

        audio_int16 = np.frombuffer(audio_chunk, np.int16)
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
                break
        else:
            silence_start = None  # Reset silence timer if voice activity is detected

    stop_listener.join()
    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    audio.terminate()
    return frames

if __name__ == "__main__":
    frames = start_recording()
    # Save the recorded audio as a WAV file
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)  # Stereo
        wf.setsampwidth(2)  # Explicitly set to 2 bytes (16-bit depth)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframesraw(b''.join(frames))

    print(f"Audio saved as {filename}")
