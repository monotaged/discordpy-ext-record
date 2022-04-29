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


from typing import (
    TYPE_CHECKING,
    Dict,
    Generic,
    Optional,
    List,
    TypeVar,
    Union,
)

from errors import AlreadyRecording
from enums import FilterStatus


if TYPE_CHECKING:
    from io import BytesIO
    from discord import User, Member, VoiceClient
    from discord.types.snowflake import Snowflake, SnowflakeList

__all__ = ("UserFilter",)

T = TypeVar("T")
ClientT = TypeVar("ClientT", bound="Client")


class UserFilter(Generic[T]):
    """
    Represents the filter for recording for each user.

    Parameters
    -----------
    client: :class:`~discord.Client`
        The client instance to use for the recording client.
    voice_client: :class:`~discord.VoiceClient`
        An object needed to record, store, and use data.
    """

    def __init__(self, client: ClientT, voice_client: VoiceClient, filtered_user: Optional[SnowflakeList] = None):
        if not filtered_user:
            filtered_user = []

        self.client: ClientT = client
        self.filtered_user: SnowflakeList = filtered_user
        self.voice_client: VoiceClient = voice_client

        self._user_audio: Dict[Snowflake, BytesIO] = {}
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

    async def start
