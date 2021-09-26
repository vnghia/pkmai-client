import threading
from typing import List, Tuple

from pkmai.room.room import Room, compute_all_listeners
from pkmai.utils.exception import raise_from_message
from pkmai.utils.type import GlobalData
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
        listeners = compute_all_listeners(self)
        listeners[good_after_msg_type] = self.__listener_good_signal
        listeners["c:"] = self.__listener_chat_timestamp

        super().__init__(conn, data, room_id, listeners, debug=debug, logs=logs)
        self.is_good = threading.Event()
        self.chats: List[Tuple[int, str, str]] = []

    # -------------------------------- User Method ------------------------------- #

    async def leave(self):
        await self.send("/noreply /leave")
        super().close()

    # --------------------------------- Listener --------------------------------- #

    def listener_noinit(self, msg: List[str]):
        raise_from_message(msg)

    def listener_title(self, msg: List[str]):
        self.title = msg[0]

    def listener_chat(self, msg: List[str]):
        self.chats.append((-1, msg[0], msg[1]))

    listener_c = listener_chat

    def __listener_good_signal(self, _: List[str]):
        self.is_good.set()

    def __listener_chat_timestamp(self, msg: List[str]):
        self.chats.append((int(msg[0]), msg[1], msg[2]))
