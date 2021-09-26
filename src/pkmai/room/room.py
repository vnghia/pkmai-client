from __future__ import annotations

import abc
import inspect
import threading
from queue import SimpleQueue
from typing import Any, Dict, List, Optional, Tuple

from pkmai.utils.exception import get_traceback
from pkmai.utils.type import GlobalData, ListernerT
from websockets.legacy.client import WebSocketClientProtocol


class Room(abc.ABC):
    @abc.abstractmethod
    def __init__(
        self,
        conn: WebSocketClientProtocol,
        data: GlobalData,
        room_id: str,
        listeners: Dict[str, ListernerT],
        debug: bool = False,
        logs: List[List[str]] = None,
    ) -> None:
        super().__init__()
        self.conn = conn
        self.data = data
        self.room_id = room_id
        self.listeners = listeners
        self.msgs: SimpleQueue[Optional[List[str]]] = SimpleQueue()
        self.exces: List[Tuple[BaseException, str]] = []
        self.logs: List[List[str]] = logs or []

        self.msgs_thread = threading.Thread(target=self.__fetch_msg, args=())
        self.msgs_thread.start()

        self.debug = debug
        if self.debug:
            self.debug_infos: List[Any] = []

    def close(self):
        if self.msgs_thread.is_alive():
            self.msgs.put_nowait(None)

    # ----------------------------------- Debug ---------------------------------- #

    def add_debug_info(self, info: Any):
        if self.debug:
            self.debug_infos.append(info)

    # -------------------------------- Communicate ------------------------------- #

    def __fetch_msg(self):
        for msg in iter(self.msgs.get, None):
            try:
                self.logs.append(msg)
                self.__process_msg(msg)
            except BaseException as exce:
                self.exces.append((exce, get_traceback(exce)))
                break

    def __process_msg(self, msg: List[str]):
        if msg[0] == "":
            listener = self.listeners.get(msg[1])
            if listener:
                listener(msg[2:])

    async def send(self, text: str):
        await self.conn.send(f"{self.room_id}|{text}")


def compute_all_listeners(room: Room) -> Dict[str, ListernerT]:
    methods = inspect.getmembers(room, inspect.ismethod)
    listeners: Dict[str, ListernerT] = {}
    for (name, method) in methods:
        if name.startswith("listener_"):
            listeners[name[len("listener_") :].replace("_", "-")] = method
    return listeners
