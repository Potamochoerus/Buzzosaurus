# Buzzosaurus

A buzzer app that can be used for quizz party games. It works on local network.
An admin hosts the game on a PC/smartphone, the other players can join. Each player can
buzz, the server will determine who buzzed first.

<img src="assets/icon.png" width="200">

 - **Phase 1** : Prototype app only working from terminal.
 - **Phase 2** : Basic UI for both server and client.
 - **Phase 3** : Basic UI unified with both server and client views.

## Repo

```
COMMUNICATION.md          # Description of messages exchanged between server and clients.
LICENCE                   # Licence file
requirements.txt          # App dependencies
src/
└── server.py             # Server class definition
app/
├── __init__.py
├── routes.py             # Route definitions
├── router.py             # Router class for navigation
└── views/
    ├── __init__.py
    ├── home.py           # Main menu view
    ├── player_login.py   # Player login/connection view
    ├── player_playing.py # Player buzzer/game view
    └── server.py         # Server hosting view
main.py                   # Updated entry point
tests/
├── test_main.py          # Test navigation between views
├── test_server.py        # Test server class works as expected
└── test_ui.py            # Test different UI work
.github/
└── workflows/
    ├── tests.yml         # Github Action to check tests pass
    └── black.yml         # Github Action to check black styling
```

## Navigation Flow

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

Terminal:

```bash
python main.py
```

## Run tests

```bash
pytest -v
```
