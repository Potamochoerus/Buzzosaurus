# Network protocol - Buzzosaurus

Communicates in **JSON on WebSocket**. The server is the only soure of truth for the buzz timing.
It adds the timestamp when the buzz is received, never the client.

## Messages Client → Serveur

### `join`
Once when a player joins.
```json
{"type": "join", "name": "Zac"}
```

### `buzz`
When a player uses the buzz button.
```json
{"type": "buzz"}
```
- Ignored if the player already buzzed. 
- Server takes the timestamp, not the client.

## Messages Serveur → Client

### `player_list`
Sent to every client, on join/quit
```json
{"type": "player_list", "players": ["Zac", "Poppy"]}
```

### `buzz_result`
Sent to everyone at each valid `buzz`. Contains the full ranking with the delta in ms.
```json
{
  "type": "buzz_result",
  "winner": "Zac",
  "ranking": [
    {"name": "Zac", "delta_ms": 0},
    {"name": "Poppy", "delta_ms": 142}
  ]
}
```

### `reset`
Sent to everyone when the admin resets the round. Erase the ranking on the server. Clients can buzz again.
```json
{"type": "reset"}
```

## Network discovery (optionnal, see `discovery.py`)
The server can be seen on the local network via mDNS/Zeroconf `_Buzzosaurus._tcp.local.`, so that clients to not have to type the IP manually.
