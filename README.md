# Buzzosaurus

A buzzer app that can be used for quizz party games. It works on local network.
An admin hosts the game on a PC/smartphone, the other players can join. Each player can
buzz, the server will determine who buzzed first.

 - **Phase 1** : Prototype app only working from terminal.
 - **Phase 2** : Basic UI for both server and client.

## Repo

- `src/server.py` : WebSocket server, timestamp source and ground truth.
- `src/client.py` : Client console to mimic a player.
- `app/server_ui.py` : Server UI.
- `app/player_ui.py` : Player UI.
- `tests/test_server.py` : Automatized tests for server logic.
- `tests/test_ui.py` : Automatized tests for UI logic.
- `COMMUNICATION.md` : Description of messages exchanged between server and clients.

## Install

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Test game from terminal

Terminal 1 (Server) :
```bash
python -m src.server
```

Terminal 2, 3, 4... (Clients) :
```bash
python -m src.client Zac
python -m src.client Poppy
```

Each player press enter to buzz. The server will stream the ranking to each client.
Type `r` + Enter to reset the server and start next round.

To try on several devices on the same network, replace `localhost` by the IP adress of the machine hosting the server.
```bash
python -m src.client Zac 192.168.1.42
```

## Test UI

Terminal 1 (Server) :
```bash
python -m app.server_ui
```

Terminal 2, 3, 4... (Clients) :
```bash
python -m app.client_ui
```

## Run tests

```bash
pytest -v
```
