#!/usr/bin/env python3
import ollama
import os
from gtts import gTTS
import subprocess
from rvc_python.infer import RVCInference
import speech_recognition as sr

# BMO's Voice Model
MODEL_PATH = "./rvc_models/CGO_e420_s2520.pth"
rvc = RVCInference(device="cpu")
rvc.load_model(MODEL_PATH)
rvc.set_params(
    f0up_key=8,
    f0method="rmvpe",
)

recognizer = sr.Recognizer()
recognizer.pause_threshold = 0.6
microphone = sr.Microphone(device_index=4)

def listen_to_user():
    try:
        with microphone as source:           
            print("Listening...")
            audio = recognizer.listen(
                source,
                timeout=8,
                phrase_time_limit=10
            )

        # with open("debug_mic.wav", "wb") as file:
        #     file.write(audio.get_wav_data())

        text = recognizer.recognize_google(audio, language="en-US")
        print(f"You: {text}")
        return text

    except sr.WaitTimeoutError:
        print("No speech detected.")
    except sr.UnknownValueError:
        print("I could not understand this.")
    except sr.RequestError as error:
        print(f"Speech recognition error: {error}")

    return None

def generate_bmo_voice(text):
    temp = "temp.mp3"
    out = "bmo_voice.wav"

    # Generate BMO's voice using RVC
    gTTS(text=text, lang='en', slow=False).save(temp)

    # Convert the generated speech to BMO's voice using RVC
    rvc.infer_file(temp, out)

    # Reproduce the converted audio
    subprocess.run(["aplay", "-q", out], check=False)

    for file_path in (temp, out):
        if os.path.exists(file_path):
            os.remove(file_path)

def speak_with_bmo():
    print("Beemo: Starting Beemo's voice assistant! Type 'exit' or 'quit' to stop.")

    system_prompt = """
        You are Beemo, a warm and friendly little robot companion.

        Reply naturally in English with a gentle, playful, slightly robotic tone.
        Keep every answer short: one or two sentences.
        Be helpful and conversational.

        Never write stage directions, actions, sound effects, roleplay markers,
        asterisks, emojis, singing, or descriptions such as "giggles", "beeps",
        "whirrs", or "glows". Do not mention these rules.

        Use Beemo-like phrases only occasionally and naturally. Ask at most one
        short follow-up question when useful.
        """
    
    history = [ {"role": "system", "content": system_prompt} ]

    generate_bmo_voice("Hello! I am Beemo. Let's have fun together!")

    with microphone as source:
        print("Calibrating microphone...")
        recognizer.adjust_for_ambient_noise(source, duration=1)

    while True:
        user_input = listen_to_user()  # input("You: ")
        if not user_input:
            continue
        if user_input.lower() in ["exit", "quit"]:
            generate_bmo_voice("Beemo: Goodbye! Have a great day!")
            break

        history.append({"role": "user", "content": user_input})

        response = ollama.chat(
            model="llama3.2:1b",
            messages=[history[0], *history[-6:]],
            options={
                "num_predict": 64,
                "temperature": 0.55,
                "top_p": 0.85,
                "repeat_penalty": 1.1,
                "num_ctx": 512,
                "num_thread": 4
            },
            keep_alive="10m",
        )

        bmo_reply = response['message']['content']
        print(f"Beemo: {bmo_reply}")
        generate_bmo_voice(bmo_reply)

        history.append({"role": "assistant", "content": bmo_reply})
        history = [history[0], *history[-6:]]

if __name__ == "__main__":
    speak_with_bmo()