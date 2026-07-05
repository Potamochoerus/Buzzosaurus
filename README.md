# Buzzosaurus

A buzzer app that can be used for quizz party games. It works on local network.
An admin hosts the game on a PC/smartphone, the other players can join. Each player can
buzz, the server will determine who buzzed first.

 - **Phase 1** : Prototype app only working from terminal.

## Repo

- `server.py` : WebSocket server, timestamp source and ground truth.
- `client.py` : Client console to mimic a player.
- `discovery.py` : Automatic discovery of the server on the local network (mDNS).
- `tests/test_server.py` : Automatized tests.
- `PROTOCOL.md` : Description of messages exchanged between server and clients.

## Install

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Test game

Terminal 1 (Server) :
```bash
python server.py
```

Terminal 2, 3, 4... (Clients) :
```bash
python client_test.py Zac
python client_test.py Poppy
```

Each player press enter to buzz. The server will stream the ranking to each client.
Type `r` + Enter to reset the server and start next round.

To try on several devices on the same network, replace `localhost` byy the IP adress of the machine hosting the server.
```bash
python client_test.py Zac 192.168.1.42
```

## Run tests

```bash
pytest -v
```
