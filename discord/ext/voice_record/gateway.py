"""
The MIT License (MIT)

Copyright (c) 2015-2021 Rapptz
Copyright (c) 2021-2022 Pycord Development
Copyright (c) 2022-present inspiredlp0 (Winston Han)

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
from __future__ import annotations

import logging
from discord.gateway import (
    DiscordVoiceWebSocket as OriginalDiscordVoiceWebSocket,
    VoiceKeepAliveHandler,
)
from typing import (
    Dict,
    Any,
)

_log = logging.getLogger(__name__)


class DiscordVoiceWebSocket(OriginalDiscordVoiceWebSocket):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ssrc_map: Dict[Any, Any] = {}

    async def received_message(self, msg: Dict[str, Any]) -> None:
        _log.debug("Voice websocket frame received: %s", msg)
        op = msg["op"]
        data = msg["d"]  # According to Discord this key is always given

        if op == self.READY:
            await self.initial_connection(data)
        elif op == self.HEARTBEAT_ACK:
            if self._keep_alive:
                self._keep_alive.ack()
        elif op == self.RESUMED:
            _log.info("Voice RESUME succeeded.")
        elif op == self.SESSION_DESCRIPTION:
            self._connection.mode = data["mode"]
            await self.load_secret_key(data)
        elif op == self.HELLO:
            interval = data["heartbeat_interval"] / 1000.0
            self._keep_alive = VoiceKeepAliveHandler(
                ws=self, interval=min(interval, 5.0)
            )
            self._keep_alive.start()
        elif op == self.SPEAKING:
            if data["ssrc"] in self.ssrc_map:
                self.ssrc_map[data["ssrc"]]["speaking"] = data["speaking"]
            else:
                self.ssrc_map.update(
                    {
                        data["ssrc"]: {
                            "user_id": int(data["user_id"]),
                            "speaking": data["speaking"],
                        }
                    }
                )

        await self._hook(self, msg)


OriginalDiscordVoiceWebSocket = DiscordVoiceWebSocket
