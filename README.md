BMO - Adventure Time AI Agent
=============================

<p align="center">
  <img src="images/BMO_front.png" alt="Fusion 360 - BMO Front" width="45%">
  <img src="images/BMO_back.png" alt="Fusion 360 - BMO Back" width="48.7%">
</p>


Electronics
------------------------

* Raspberry Pi 5 (w/ active cooler)
* Freenove 5 inch touchscreen monitor
* Camera Module 3 Wide NoIR

Future Additions
------------------

* USB microphone
* Speaker
* Custom PCB for button control (using Raspberry Pi 5 GPIO)


Setup Venv
------------

sudo add-apt-repository ppa:deadsnakes/ppa -y

sudo apt update

sudo apt install python3.10 python3.10-venv python3.10-dev -y


python3.10 -m venv venv


source venv/bin/activate


pip install --upgrade pip setuptools wheel

pip install "pip<24.1"

pip install ollama gTTS rvc-python


Ollama
----------

Install Ollama (open-source platform that lets you download and run large language models (LLMs) directly on your own local computer): 


curl -fsSL https://ollama.com/install.sh | sh


Download the model (Meta's Llama 3.2 model 3 billion parameters):


ollama run llama3.2:3b 


pip install ollama


Give BMO a voice
--------------------

sudo apt update && sudo apt install mpg321 -y

pip install gTTS


Cloning BMO voice
-----------------

sudo apt install ffmpeg -y 

pip install --upgrade pip setuptools wheel cython

pip install rvc-python

cd ~/bmo

mkdir -p rvc_models

curl -L -o rvc_models/BMO.zip https://huggingface.co/Freaky98/CGO-adventure-time-BMO-rvc-v2-420e/resolve/main/CGO-adventure-time-BMO-rvc-v2-420e.zip

unzip rvc_models/BMO.zip

rm rvc_models/BMO.zip