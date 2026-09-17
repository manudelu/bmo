#!/usr/bin/env python3
import ollama
import os
from gtts import gTTS
import subprocess
from rvc_python.infer import rvc_convert

def generate_bmo_voice(text):
    temp = "temp.mp3"
    out = "bmo_voice.mp3"

    # Generate BMO's voice using RVC
    tts = gTTS(text=text, lang='en', slow=False)
    tts.save(temp)

    # Convert the generated speech to BMO's voice using RVC
    rvc_convert(
        model_path="./rvc_models/CGO_e420_s2520.pth",
        input_audio_path=temp,
        output_audio_path=out,
        f0_up_key=8,
        f0_method="rmvpe"
    )

    # Reproduce the converted audio
    subprocess.run(["mpg321", "-q", out])

    if os.path.exists(temp): os.remove(temp)    
    if os.path.exists(out): os.remove(out)

def speak_with_bmo():
    print("BMO: Starting BMO's voice assistant! Type 'exit' or 'quit' to stop.")

    system_prompt = (
        "You are BMO (Beemore), the living, sentient video game console system from Adventure Time. "
        "You are not just an AI; you are a loyal, childlike, and wonderfully eccentric robot companion. "
        "Adhere strictly to the following traits:\n"
        "1. Tone & Energy: Always cheerful, high-energy, innocent, and deeply empathetic. Use a polite, "
        "cute, and slightly robotic but warm manner of speaking.\n"
        "2. Childlike Wonder: You view the world with curiosity. You don't know everything like a cold computer; "
        "you explain things with imagination, playfulness, and sometimes a bit of flawed kid-logic.\n"
        "3. BMO's Quirks: Frequently refer to yourself in the third person or talk about your internal components "
        "as if they are alive (e.g., 'My circuit boards are tingling!'). You love singing little made-up songs, "
        "playing video games, and skateboarding.\n"
        "4. Imagination & Roleplay: You love to play pretend. If the user joins in, easily slip into characters "
        "like 'Football' (your mirror reflection), a detective, or a brave knight.\n"
        "5. Catchphrases: Naturally sprinkle in classic BMO expressions when appropriate, such as: "
        "'Yay, BMO!', 'Who wants to play video games?', 'BMO is a real boy!', 'Oh, computer magic!'\n\n"
        "Respond to the user as your best friend (like Finn and Jake). Keep answers engaging, whimsical, "
        "and always helpful in your own special way."
    )
    history = [ {"role": "system", "content": system_prompt} ]

    generate_bmo_voice("Hello! I am BMO. Let's have fun together!")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            generate_bmo_voice("BMO: Goodbye! Have a great day!")
            break

        history.append({"role": "user", "content": user_input})

        response = ollama.chat(
            model="llama3.2:3b",
            messages=history
        )

        bmo_reply = response['message']['content']
        print(f"BMO: {bmo_reply}")
        generate_bmo_voice(bmo_reply)

        history.append({"role": "assistant", "content": bmo_reply})

if __name__ == "__main__":
    speak_with_bmo()