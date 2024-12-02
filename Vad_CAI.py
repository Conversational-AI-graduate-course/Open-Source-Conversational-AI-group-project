import struct
import pyaudio
#pip3 install pvporcupinedemo
#import pvporcupine
import wave
import os
import time

#Porcupine requires a valid Picovoice AccessKey at initialization. 
#AccessKey acts as your credentials when using Porcupine SDKs. 
#You can get your AccessKey for free. Make sure to keep your AccessKey secret.
#Signup or Login to Picovoice Console to get your AccessKey OR Just go to github and follow the process

# Set the device index and sample rate based on the previous output
device_index = 9  # You selected this device
sample_rate = 48000  # The sample rate that worked

# Folder to save the WAV files
folder_name = "recordings"

# Create the folder if it doesn't exist
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

# Generate a unique file name with a timestamp
timestamp = time.strftime("%Y%m%d-%H%M%S")  # Format: YYYYMMDD-HHMMSS
filename = os.path.join(folder_name, f"output_{timestamp}.wav")

# Initialize PyAudio
audio = pyaudio.PyAudio()

porcupine = None

# Open the audio stream
stream = audio.open(format=pyaudio.paInt16,
                    channels=2,  # Stereo input (2 channels)
                    rate=sample_rate,
                    input=True,
                    input_device_index=device_index,
                    frames_per_buffer=1024)

# Record audio for 10 seconds
print("Recording...")
frames = []

for i in range(0, int(sample_rate / 1024 * 10)):  # 10 seconds of audio
    data = stream.read(1024)
    frames.append(data)
    
# Debug: Print length of data captured
print(f"Captured {len(data)} bytes")

# Stop and close the stream
stream.stop_stream()
stream.close()
audio.terminate()

# Save the recorded audio as a WAV file
with wave.open(filename, 'wb') as wf:
    wf.setnchannels(2)  # Stereo
    wf.setsampwidth(2)  # Explicitly set to 2 bytes (16-bit depth)
    wf.setframerate(sample_rate)
    wf.writeframes(b''.join(frames))

print(f"Audio saved as {filename}")



# porcupine = pvporcupine.create(keywords=["Sedric", "Computer"])

# while True:
# pcm = stream.read(porcupine.frame_length)
# pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

# keyword_index = porcupine.process(pcm)

# if keyword_index >= 0:
#     print("Hotword Detected")
#     speak("Computer online")
