# Voice Activation and Wake Word

After starting this model will wait until wakeword recognition to record user input and will end this recording after 2 seconds of silence. The recording will be saved in the `recordings` folder. 

## Custom Wake Word Model

This application allows you to specify a custom wake word model to be used during runtime. By default, the wake word is set to **"Yoh Dewd"**. 

## How to Run

To run the application with a custom wake word model, place your `.tflite` model file in the `wakeword_model` folder and specify the wake word using the `--wake_word` argument.

### Example Command:

```bash
python3 main.py --wake_word "Yoh Dewd"
