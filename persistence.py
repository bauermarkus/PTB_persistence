from typing import Any, Dict, Optional
from telegram.ext import BasePersistence, PersistenceInput
from telegram.ext._utils.types import CDCData, ConversationDict, ConversationKey

import logging

class Persistence(BasePersistence):
    def __init__(self, users: list, cursor):

        self._store_data = PersistenceInput(
            True, # bot_data
            False, # chat_data
            False, # user_data
            False,  # callback_data
        )

        super().__init__(store_data=self._store_data, update_interval=1)
        self._users = users
        self._cursor = cursor

    async def get_bot_data(self):
        return {'users': self._users, 'cursor': self._cursor}
    async def update_bot_data(self, data) -> None:
        print("Update bot data", data)
    async def refresh_bot_data(self, bot_data) -> None:
        print("Refresh:",bot_data)
        

    async def get_chat_data(self) -> Dict[int, Any]:
        pass
    async def update_chat_data(self, chat_id: int, data: Any) -> None:
        pass
    async def refresh_chat_data(self, chat_id: int, chat_data: Any) -> None:
        pass
    async def drop_chat_data(self, chat_id: int) -> None:
        pass

    async def get_user_data(self) -> Dict[int, Any]:
        pass
    async def update_user_data(self, user_id: int, data: Any) -> None:
        pass
    async def refresh_user_data(self, user_id: int, user_data: Any) -> None:
        pass
    async def drop_user_data(self, user_id: int) -> None:
        pass

    async def get_callback_data(self) -> CDCData or None:
        pass
    async def update_callback_data(self, data: CDCData) -> None:
        pass

    async def get_conversations(self, name: str) -> ConversationDict:
        pass
    async def update_conversation(self, name: str, key: ConversationKey, new_state: object or None) -> None:
        pass

    async def flush(self) -> None:
        pass

