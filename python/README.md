# Training Session in Python

## Intro

The training in Python will cover all the concepts you need to be aware of to start using IOTICS. In particular the training will be divided into:
- Morning Session
  - Create a Twin Receiver
  - Create a Twin Sender
- Afternoon Session
  - Create a Publisher Connector
  - Create a Follower Connector

More details will be given on the day of the training. For now we only need you to setup your laptop so you come prepared for the code excercises.

## Laptop Setup

1.  Install [Python](https://www.python.org/downloads/) (3.7+) on your machine;
2.  Create a new Python virtual environment:
```bash
ON LINUX:
python3 -m venv iotics_training
ON WINDOWS:
python -m venv iotics_training
```
3.  Activate the virtual environment:
```bash
ON LINUX:
source iotics_training/bin/activate
ON WINDOWS:
.\iotics_training\Scripts\Activate.bat
ON WINDOWS (powershell):
.\iotics_training\Scripts\Activate.ps1
```
4.  Download the IOTICS Stomp Library from [this](https://github.com/Iotic-Labs/iotics-host-lib/blob/master/stomp-client/iotic.web.stomp-1.0.6.tar.gz) link on your local machine;
5.  Install the above library in your virtual environment along with the Identity Library and the gRPC Python Client Lib:
```bash
pip install -U pip setuptools wheel iotics-identity iotic.web.stomp-1.0.6.tar.gz iotics-grpc-client
```
