from __future__ import annotations

import asyncio
import json
import ssl
from typing import Dict, List, Optional

import requests
from websockets.client import connect as wsconnect
from websockets.legacy.client import WebSocketClientProtocol

from pkmai.battle.battle import Battle
from pkmai.room.chat import Chat
from pkmai.room.room import Room, compute_all_listeners
from pkmai.utils.exception import get_traceback


class Client(Room):

    # ------------------------- Constructor / Destructor ------------------------- #

    def __init__(self, conn: WebSocketClientProtocol, debug: bool) -> None:
        super().__init__(conn, {}, "", compute_all_listeners(self), debug=debug)
        self.rooms: Dict[str, Room] = {self.room_id: self}
        self.battles: Dict[str, Battle] = {}
        self.chats: Dict[str, Chat] = {}
        self.found_battle = asyncio.Event()
        self.found_battle_id: Optional[str] = None
        self.recv_task = asyncio.create_task(self.__fetch_recv())

    @classmethod
    async def init(cls, verify_ssl: bool = True, debug: bool = False) -> Client:
        if not verify_ssl:
            ssl_context = ssl._create_unverified_context()
        else:
            ssl_context = ssl.create_default_context()
        conn = await wsconnect(
            "wss://sim.smogon.com/showdown/websocket", ssl=ssl_context
        )
        self = cls(conn, debug)
        return self

    async def close(self):
        super().close()
        await self.conn.close()
        await self.recv_task

    # -------------------------------- Communicate ------------------------------- #

    async def __fetch_recv(self):
        try:
            while True:
                raw = await self.conn.recv()
                lines = raw.splitlines()
                if lines[0][0] != ">":
                    room_id = ""
                else:
                    room_id = lines[0][1:]
                    if room_id not in self.rooms:
                        battle = Battle(self.conn, self.data, room_id, self.debug)
                        self.add_debug_info(
                            ("room_id not in self.rooms", room_id not in self.rooms)
                        )
                        self.found_battle_id = room_id
                        self.rooms[room_id] = battle
                        self.battles[room_id] = battle
                        self.found_battle.set()
                        self.add_debug_info(
                            ("self.found_battle.is_set()", self.found_battle.is_set())
                        )
                    lines = lines[1:]
                for line in lines:
                    if not line:
                        continue
                    self.rooms[room_id].msgs.put_nowait(line.split("|"))
        except asyncio.CancelledError:
            await self.conn.close()
            return
        except BaseException as exce:
            self.exces.append((exce, get_traceback(exce)))

    # -------------------------------- User Method ------------------------------- #

    async def login(self, username: str, password: str, retry: int = 1):
        for _ in range(retry):
            if "challstr" not in self.data:
                await asyncio.sleep(1)
            else:
                break
        if "challstr" not in self.data:
            raise ValueError("Missing challstr")
        resp = requests.post(
            "https://play.pokemonshowdown.com/action.php?",
            json={
                "act": "login",
                "name": username,
                "pass": password,
                "challstr": self.data["challstr"],
            },
        )
        resp.raise_for_status()
        data = json.loads(resp.text[1:])
        await self.send(f"/trn {username},0,{data['assertion']}")
        self.data["username"] = username

    async def join_chat(self, room_id: str) -> Chat:
        room = Chat(self.conn, self.data, room_id, self.debug)
        self.rooms[room_id] = room
        self.chats[room_id] = room
        await self.send(f"/join {room_id}")
        return room

    async def search_battle(
        self,
        format: str,
        team: str = "null",
        timeout: Optional[float] = None,
    ) -> Battle:
        await self.send(f"/utm {team}")
        await self.send(f"/search {format}")
        try:
            await asyncio.wait_for(self.found_battle.wait(), timeout=timeout)
            self.found_battle.clear()
            found_battle_id = self.found_battle_id
            if not found_battle_id:
                raise ValueError("Missing found_battle_id")
            else:
                self.found_battle_id = None
                return self.battles[found_battle_id]
        except asyncio.TimeoutError:
            await self.send("/cancelsearch")
            raise TimeoutError(
                f"Timeout exceeded while searching for battle (format: {format}, team: {team})"
            )

    async def accept_challenge(
        self, challenger: str, team: str = "null", timeout: Optional[float] = None
    ) -> Battle:
        await self.send(f"/utm {team}")
        await self.send(f"/accept {challenger}")
        try:
            await asyncio.wait_for(self.found_battle.wait(), timeout=timeout)
            self.found_battle.clear()
            found_battle_id = self.found_battle_id
            if not found_battle_id:
                raise ValueError("Missing found_battle_id")
            else:
                self.found_battle_id = None
                return self.battles[found_battle_id]
        except asyncio.TimeoutError:
            raise TimeoutError(
                f"Timeout exceeded while accepting challenge from {challenger}"
            )

    # --------------------------------- Listener --------------------------------- #

    def listener_challstr(self, msg: List[str]):
        self.data["challstr"] = "|".join(msg)

    def listener_updateuser(self, msg: List[str]):
        self.data["username"] = msg[0][1:]
