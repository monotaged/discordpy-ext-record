"""
The MIT License (MIT)

Copyright (c) 2021-2022 Pycord Development
Copyright (c) 2021-present inspiredlp0 (Winston Han)

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

import io
import struct
import logging
import asyncio
from discord import File
from select import select
from .enums import FilterStatus
from .errors import AlreadyRecording, NotRecording
from .opus import OpusStruct, Xsalsa20Decrypt, DecodeManager
from typing import (
    TYPE_CHECKING,
    Dict,
    Generic,
    Optional,
    TypeVar,
    Union,
    Any,
)


if TYPE_CHECKING:
    from .tree import RecordFileTree
    from .gateway import DiscordVoiceWebSocket
    from discord import User, Member, Client, VoiceClient
    from discord.types.snowflake import Snowflake, SnowflakeList

__all__ = ("UserFilter",)

_log = logging.getLogger(__name__)

T = TypeVar("T")
SinkT = TypeVar("SinkT", bound="BaseSink", covariant=True)


class UserFilter(Generic[T]):
    """
    Represents the filter for recording for each user.

    Parameters
    -----------
    client: :class:`~discord.Client`
        The client instance to use for the recording client.
    voice_client: :class:`~discord.VoiceClient`
        An object needed to record, store, and use data.
    filtered_user: :class:`~discord.types.snowflake.SnowflakeList`
        The list of user IDs.
    """

    def __init__(
        self,
        client: Client,
        voice_client: VoiceClient,
        filtered_user: Optional[SnowflakeList] = None,
    ):
        if not filtered_user:
            filtered_user = []

        self.client: Client = client
        self.filtered_user: SnowflakeList = filtered_user
        self.voice_client: VoiceClient = voice_client
        self.voice_websocket: DiscordVoiceWebSocket = voice_client.ws

        self._user_audio_data: Dict[Snowflake, io.BytesIO] = {}
        self._user_audio_files: Dict[Snowflake, io.BytesIO]
        self._user_audio_timestamp: Dict[Any, Any] = {}
        self._decoder: Optional[DecodeManager] = None
        self._sink: Optional[SinkT] = None
        self._record_time: float = 0
        self._recoding: bool = False
        self._paused: bool = False

    @property
    def status(self) -> FilterStatus:
        """Displays the status of the filter.
        The filter's status is returned as <enum 'FilterStatus'>, with recording, stopped and paused.

        Returns
        --------
        :class:`FilterStatus`
            An enum that displays the status in the filter.
        """

        if self._recoding:
            return FilterStatus.recording
        elif self._paused:
            return FilterStatus.paused

        return FilterStatus.stopped

    def toggle_pause(self) -> None:
        """Pauses or unpauses the recording.
        Must be already recording.

        Raises
        ------
        NotRecording
            You cannot use toggle_pause function to the filter because they are not recording
        """

        if not self._recoding:
            raise NotRecording("Not currently recording audio.")
        self._paused = not self._paused

    def add_user(self, user: Union[User, Member], /) -> None:
        """Add user to the filter.
        ``user`` parameter is positional-only.

        Parameters
        -----------
        user: Union[User, Member]
            The user object to add to the filter.

        Raises
        ------
        AlreadyRecording
            You cannot add users to the filter because they are already recording.
        """

        if self._recoding:
            raise AlreadyRecording(
                "You cannot add users to the filter because they are already recording."
            )

        self.filtered_user.append(user.id)

    def remove_user(self, user: Union[User, Member], /) -> None:
        """Remove user to the filter.
        ``user`` parameter is positional-only.

        Parameters
        -----------
        user: Union[User, Member]
            The user object to remove to the filter.

        Raises
        ------
        AlreadyRecording
            You cannot add users to the filter because they are already recording.
        """

        if self._recoding:
            raise AlreadyRecording(
                "You cannot remove users to the filter because they are already recording."
            )

        self.filtered_user.remove(user.id)

    async def start(self, sink: SinkT) -> None:
        """|coro|
        Start recording in the appropriate voice client.

        Parameters
        -----------
        sink
            Sink is an object that records the format and the data that was transferred.

        Raises
        ------
        AlreadyRecording
            You cannot add users to the filter because they are already recording.
        """

        if self._recoding:
            raise AlreadyRecording(
                "You cannot starting record because they are already recording."
            )
        await self._empty_socket()
        self.client.dispatch("record_ready")

        self._decoder = DecodeManager(user_filter=self)
        await self._decoder.start()
        self._recoding = True
        self._sink = sink

    async def stop(self) -> RecordFileTree:
        """|coro|

        Stops the recording.
        Must be already recording.

        Raises
        ------
        NotRecording
            You cannot use stop function to the filter because they are not recording.

        Returns
        --------
        :class:`RecordFileTree`
            Recorded data files file the container converts an object.
        """
        if not self._recoding:
            raise NotRecording("Not currently recording audio.")
        await self._decoder.stop()
        self._recoding = False
        self._paused = False
        return RecordFileTree(
            files={
                snowflake: File(
                    fp=await self._sink.format_audio(bytes_file.raw),
                    filename=f"audio.{self._sink.extension}",
                )
                for snowflake, bytes_file in self._user_audio_data.values()
            }
        )

    async def unpack_audio_packet(self, data: bytes) -> None:
        """|coro|

        Takes an audio packet received from Discord and decodes it into pcm audio data.
        If there are no users talking in the channel, `None` will be returned.

        You must be connected to receive audio.

        Parameters
        ---------
        data: :class:`bytes`
            Bytes received by Discord via the UDP connection used for sending and receiving voice data.
        """

        if 200 <= data[1] <= 204:
            # RTCP received.
            # RTCP provides information about the connection
            # as opposed to actual audio data, so it's not
            # important at the moment.
            return
        if self._paused:
            return

        packed_data = FilteredDataPack(data=data)

        if (
            packed_data.decrypted_data(mode=self.voice_client.mode) == b"\xf8\xff\xfe"
        ):  # Frame of silence
            return

    async def _empty_socket(self) -> None:
        while True:
            ready, _w_list, _x_list = select([self.voice_client.socket], [], [], 0.0)
            if not ready:
                break
            for socket in ready:
                socket.recv(4986)

    async def _receive_packet(self) -> None:
        self._user_audio_timestamp.clear()

        while self._recoding:
            ready, _, error = select(
                [self.voice_client.socket], [], [self.voice_client.socket], 0.01
            )
            if not ready and error:
                _log.error(f"Socket error: {error}")
            elif not ready:
                continue

            try:
                data = self.voice_client.socket.recv(4096)
            except OSError:
                await self.stop()
                continue

            await self.unpack_audio_packet(data=data)

            for bytes_file in self._user_audio_data.values():
                bytes_file.seek(0)

    async def receive_decoded_packet(self, packed_data: FilteredDataPack) -> None:
        if packed_data.ssrc not in self._user_audio_timestamp:
            self._user_audio_timestamp.update({packed_data.ssrc: packed_data.timestamp})
            # Add silence when they were not being recorded.
            silence = 0
        else:
            silence = (
                packed_data.timestamp
                - self._user_audio_timestamp[packed_data.ssrc]
                - 960
            )
            self._user_audio_timestamp[packed_data.ssrc] = packed_data.timestamp

        decoded_data = struct.pack(
            "<h", 0
        ) * silence * OpusStruct.CHANNELS + packed_data.decrypted_data(
            mode=self.voice_client.mode
        )
        while packed_data.ssrc not in getattr(self.voice_client.ws, "ssrc_map"):
            await asyncio.sleep(0.05)
        user_audio_data = io.BytesIO()
        if (
            self.voice_websocket.ssrc_map[packed_data.ssrc]["user_id"]
            not in self._user_audio_data.keys()
        ):
            self._user_audio_data.update(
                {
                    self.voice_websocket.ssrc_map[packed_data.ssrc][
                        "user_id"
                    ]: user_audio_data
                }
            )
            bytes_file = self._user_audio_data[
                self.voice_websocket.ssrc_map[packed_data.ssrc]["user_id"]
            ]
            bytes_file.write(decoded_data)


class FilteredDataPack:
    """Handles raw data from Discord so that it can be decrypted and decoded to be used."""

    def __init__(self, data: bytes) -> None:
        self._data = bytearray(data)
        self.xsalsa_20_decrypt = Xsalsa20Decrypt()
        self.user_id: Optional[Snowflake] = None

        unpacker = struct.Struct(">xxHII")
        self.sequence, self.timestamp, self.ssrc = unpacker.unpack_from(self.header)
        self.decode_data: Optional[bytes] = None

    @property
    def header(self) -> bytes:
        return self._data[:12]

    @property
    def data(self) -> bytes:
        return self._data[12:]

    def decrypted_data(self, mode: str) -> Optional[bytes]:
        return getattr(self.xsalsa_20_decrypt, f"_decrypt_{mode}")(
            self.header, self.data
        )
