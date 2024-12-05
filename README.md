To run listening for all available wakewords: 
    python3 Wakeword_VAD.py

To run with a specific wakeword, specify modelpath in command line: 

for "Alexa": 
    python3 Wakeword_VAD.py --model_path /home/USERNAME/.local/lib/python3.10/site-packages/openwakeword/resources/models/alexa_v0.1.tflite
for "Hey Mycroft":
    python3 Wakeword_VAD.py --model_path /home/USERNAME/.local/lib/python3.10/site-packages/openwakeword/resources/models/hey_mycroft_v0.1.tflite