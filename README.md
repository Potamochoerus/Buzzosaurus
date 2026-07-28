# Buzzosaurus

![GitHub tag](https://img.shields.io/github/v/tag/USERNAME/REPO)

A buzzer app that can be used for quizz party games. It works on local network.
An admin hosts the game on a PC/smartphone, the other players can join. Each player can
buzz, the server will determine who buzzed first.

<img src="assets/icon.png" width="200">

## App Navigation Flow

```
HOME
├── → SERVER (host button)
└── → PLAYER_LOGIN (join button)
      └── → PLAYER_PLAYING (on successful connection)
```

## Install

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run the app locally

```bash
python main.py
```

## Run tests

```bash
pytest -v
```
