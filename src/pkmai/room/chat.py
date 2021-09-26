import threading
from typing import Dict, List, Tuple

from pkmai.room.room import Room
from pkmai.utils.exception import raise_from_message
from pkmai.utils.type import GlobalData, ListernerT
from websockets.legacy.client import WebSocketClientProtocol


class Chat(Room):
    def __init__(
        self,
        conn: WebSocketClientProtocol,
        data: GlobalData,
        room_id: str,
        debug: bool = False,
        logs: List[List[str]] = None,
        good_after_msg_type: str = "init",
    ) -> None:
        listeners: Dict[str, ListernerT] = {
            good_after_msg_type: self.__set_good,
            "noinit": self.__noinit,
            "title": self.__title,
            "c": self.__chat,
            "chat": self.__chat,
            "c:": self.__chat_timestamp,
        }
        super().__init__(conn, data, room_id, listeners, debug=debug, logs=logs)
        self.is_good = threading.Event()
        self.chats: List[Tuple[int, str, str]] = []

    # -------------------------------- User Method ------------------------------- #

    async def leave(self):
        await self.send("/noreply /leave")
        super().close()

    # --------------------------------- Listener --------------------------------- #

    def __set_good(self, _: List[str]):
        self.is_good.set()

    def __noinit(self, msg: List[str]):
        raise_from_message(msg)

    def __title(self, msg: List[str]):
        self.title = msg[0]

    def __chat(self, msg: List[str]):
        self.chats.append((-1, msg[0], msg[1]))

    def __chat_timestamp(self, msg: List[str]):
        self.chats.append((int(msg[0]), msg[1], msg[2]))
