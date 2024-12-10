import os
import time
import src.wakeword as wakeword


folder_name = "recordings"
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

# Generate a unique file name with a timestamp
timestamp = time.strftime("%Y%m%d-%H%M%S")  # Format: YYYYMMDD-HHMMSS
filename = os.path.join(folder_name, f"output_{timestamp}.wav")

frames = wakeword.start_listening()

wakeword.save_frames_to_wav(frames, filename)


