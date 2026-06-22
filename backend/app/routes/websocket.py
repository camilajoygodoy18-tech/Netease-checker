from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import asyncio
import json

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}  # user_id -> set of ws

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)

    def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)

    async def send_personal_message(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            for ws in self.active_connections[user_id]:
                try:
                    await ws.send_json(message)
                except:
                    pass

    async def broadcast(self, message: dict):
        for user_set in self.active_connections.values():
            for ws in user_set:
                try:
                    await ws.send_json(message)
                except:
                    pass

manager = ConnectionManager()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            # handle incoming messages (e.g., start check, stop)
            try:
                msg = json.loads(data)
                if msg.get("action") == "start_check":
                    # spawn background task with provided combos/proxies
                    # we'll implement in checks.py and call manager.send_personal_message
                    pass
            except:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)