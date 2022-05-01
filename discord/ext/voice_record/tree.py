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

from .filter import UserFilter
from typing import (
    List,
    Dict,
    Generic,
    TypeVar,
    Optional,
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from discord import File, VoiceClient
    from discord.types.snowflake import Snowflake, SnowflakeList

__all__ = ("VoiceFilterTree", "RecordFileTree")

ClientT = TypeVar("ClientT", bound="Client")


class VoiceFilterTree(Generic[ClientT]):
    """Represents a container that holds user filters for recording clients.

    Parameters
    -----------
    client: :class:`~discord.Client`
        The client instance to use for the recording client.
    """

    def __init__(self, client: ClientT) -> None:
        self.client: ClientT = client
        self._user_filters: Dict[int, UserFilter] = {}

    def get(self, id: int, /) -> Optional[UserFilter]:
        """Returns a <.UserFilter> object for a specific guild

        ``id`` parameter is positional-only.

        Parameters
        -----------
        id: int
            The ID of a particular guild.
        """
        return self._user_filters.get(id, None)

    def __delitem__(self, key: int) -> None:
        del self._user_filters[key]

    async def create_filter(
        self,
        filter: SnowflakeList,
        voice_client: VoiceClient,
        guild: Snowflake,
    ) -> UserFilter:
        """|coro|

        Creates and returns a <.UserFilter> object corresponding to a specific guild.

        Parameters
        -----------
        filter: SnowflakeList
            The list of user IDs to use when creating <.UserFilter> objects.
        voice_client: VoiceClient
            An object needed to record, store, and use data.
        guild: Snowflake
            Guild id to correspond to a specific guild.

        Returns
        --------
        :class:`UserFilter`
            User filter object for recording.
        """
        user_filter = UserFilter(
            client=self.client, voice_client=voice_client, filtered_user=filter
        )
        self._user_filters[guild] = user_filter
        return user_filter


class RecordFileTree:
    """Represents a container that holds user record file for recording clients.

    Parameters
    -----------
    files: Dict[discord_record.types.snowflake.Snowflake, discord.File]
        File data from the user audio recording.
    """

    def __init__(self, files: Dict[Snowflake, File]) -> None:
        self._files: Dict[Snowflake, File] = files

    def __len__(self) -> int:
        return len(self._files)

    def all(self) -> Optional[List[File]]:
        """Returns data from all files."""

        return self._files.values() or None

    def get(self, id: int, /) -> Optional[File]:
        """Returns a recorded file for a specific user.

        ``id`` parameter is positional-only.
        """
        return self._files.get(id, None)
