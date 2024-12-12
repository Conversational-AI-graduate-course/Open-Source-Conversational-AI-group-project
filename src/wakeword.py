import os
import time
import wave
import threading
import numpy as np
import pyaudio
import torch
from openwakeword.model import Model

class WakeWordListener:
    """
    Class for detecting a wake word using a pre-trained model, recording audio upon detection,
    and saving the audio to a file. 

    Attributes:
        model_path (str): Path to the wake word detection model.
        silence_threshold (float): Confidence threshold below which audio is considered silence. Default is 0.5.
        silence_duration (float): Duration in seconds of continuous silence required to stop recording. Default is 2.0.
        rate (int): Sampling rate for the audio stream. Default is 16000.
        chunk_size (int): Size of audio chunks to read from the stream. Default is 800.
        num_samples (int): Number of samples for buffering audio chunks. Default is 512.
    """
    def __init__(self, model_path, silence_threshold=0.5, silence_duration=2.0, rate=16000, chunk_size=800, num_samples = 512):
        self.model_path = model_path
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration
        self.rate = rate
        self.chunk_size = chunk_size
        self.num_samples = num_samples

        self.audio = pyaudio.PyAudio()
        self.model = self.load_wakeword_model(model_path)
        self.continue_recording = True
        self.silence_detected = False
        self.frames = []
        self.buffer = np.array([], dtype=np.int16)

        self.vad_model, self.utils = torch.hub.load(
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad',
            force_reload=True
        )
        self.get_speech_timestamps = self.utils[0]
        self.stream = None
        

    def load_wakeword_model(self, model_path):
        """
        Loads the wake word detection model.

        Args:
            model_path (str): Path to the wake word detection model.

        Returns:
            Model: The loaded wake word detection model.

        Raises:
            FileNotFoundError: If the specified model path does not exist.
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model path does not exist: {model_path}")
        return Model(wakeword_models=[model_path], inference_framework="tflite")

    def listen_for_wakeword(self):
        """
        Listen for the wake word

        Returns:
            None
        """
        
        print("\n\n")
        print("#"*100)
        print("Listening for wakewords...")
        print("#"*100)
        print("\n"*(3))
        wakeword_detected = False
        while not wakeword_detected:
            audio_chunk = self.stream.read(self.chunk_size)
        
            audio_sign = np.frombuffer(audio_chunk, dtype=np.int16)

            self.model.predict(audio_sign)

            for mdl in self.model.prediction_buffer.keys():
                
                scores = list(self.model.prediction_buffer[mdl])
                curr_score = format(scores[-1], '.20f').replace("-", "")
                if float(curr_score) >= 0.5: 
                    wakeword_detected = True
                    print("Wakeword detected")
    
    def stop_recording(self):
        """
        Stops the recording process when silence condition is met.

        Returns: 
            None
        """
       
        while self.continue_recording and not self.silence_detected:
            time.sleep(0.1)  # avoid busy waiting

    # Provided by Alexander Veysov
    def int2float(self, sound):
        """
        Converts an integer audio signal to a floating-point representation.

        Args:
            sound (np.ndarray): The input audio signal as a NumPy array of integer values.

        Returns:
            np.ndarray: A normalized floating-point representation of the audio signal, with dtype `float32`.
        """
        abs_max = np.abs(sound).max()
        sound = sound.astype('float32')
        if abs_max > 0:
            sound *= 1/32768
        sound = sound.squeeze()  # depends on the use case
        return sound

    def record_audio(self):
        """
        Records audio until the specified duration of silence is detected

        Returns:
            list: A list of recorded audio frames.
        """
        
        print("\n\n")
        print("#"*100)
        print("Recording...")
        print("#"*100)
   
        silence_start = None
        self.frames = []
        self.continue_recording = True
        stop_listener = threading.Thread(target=self.stop_recording)
        stop_listener.start()

        while self.continue_recording:
            audio_chunk = self.stream.read(self.chunk_size)
            
            # In case you want to save the audio later
            self.frames.append(audio_chunk)

            # Buffering required to fix numsample and chunk mismatch of different models
            audio_int16 = np.frombuffer(audio_chunk, np.int16)
            self.buffer = np.concatenate((self.buffer, audio_int16))
            audio_int16 = self.buffer[:self.num_samples]
            self.buffer = self.buffer[self.num_samples:]

            audio_float32 = self.int2float(audio_int16)
                
            new_confidence = self.vad_model(torch.from_numpy(audio_float32), self.rate).item()

            # Check for silence
            if new_confidence < self.silence_threshold:
                if silence_start is None:
                    silence_start = time.time()  # Silence start
                elif time.time() - silence_start >= self.silence_duration:
                    print("Detected 2 seconds of silence. Stopping recording.")
                    self.silence_detected = True  
                    stop_listener.join()

                    return self.frames
                    
            else:
                silence_start = None  # Reset silence timer if voice activity is detected

    
    continue_recording = False 
    
    def save_to_wav(self, filename):
        """
        Saves recorded audio frames to a WAV file.

        Args:
            filename (str): The name of the output WAV file.

        Returns:
            None
        """
        
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(self.frames))
        print(f"Audio saved to {filename}")