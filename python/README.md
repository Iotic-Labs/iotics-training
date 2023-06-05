# Training Session in Python

## Intro

The training in Python will cover all the concepts you need to be aware of to start using IOTICS. In particular the training will be divided into:
- Morning Session
  - Create a Twin Receiver
  - Create a Twin Sender
- Afternoon Session
  - Create a Publisher Connector
  - Create a Synthesiser Connector

More details will be given on the day of the training. For now we only need you to set up your laptop so you come prepared for the training.

## Laptop Setup

Before the Training Session, you first need to create and activate your Python virtual environment. After installing Python (version <= 3.10), you can do that automatically by following the instructions below:
```bash
make setup
source ./iotics_training/bin/activate
```

Alternatively you can follow the manual steps below:

1.  Create a new Python virtual environment:
    - Linux: `python3 -m venv iotics_tutorials`
    - Windows: `python -m venv iotics_tutorials`

2.  Activate the virtual environment:
    - Linux: `source ./iotics_tutorials/bin/activate`
    - Windows: `.\iotics_tutorials\Scripts\Activate.bat`
    - Windows (powershell): `.\iotics_tutorials\Scripts\Activate.ps1`

3.  Download the IOTICS Stomp Library from [this](https://github.com/Iotic-Labs/iotics-host-lib/blob/master/stomp-client/iotic.web.stomp-1.0.6.tar.gz) link to the `python` folder of this repository;
4.  Install the required dependencies: `pip install -r requirements.txt`
