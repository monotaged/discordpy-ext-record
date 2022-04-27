from __future__ import annotations
import io


from typing import (
    TYPE_CHECKING,
    Dict,
    Generic,
    List,
    TypeVar,
    Union,
)

from errors import AlreadyRecording


if TYPE_CHECKING:
    from discord import User, Member, VoiceClient

__all__ = ("UserFilter",)

ClientT = TypeVar("ClientT", bound="Client")

T = TypeVar("T")


class UserFilter(Generic[T]):
    """
    Represents the filter for recording for each user.

    Parameters
    -----------
    client: :class:`~discord.Client`
        The client instance to use for the recording client.
    """

    def __init__(self, client: ClientT, voice_client: VoiceClient):
        self.client: ClientT = client
        self.filtered_user: List[int] = []
        self.voice_client: VoiceClient = voice_client

        self._user_audio: Dict[int, io.BytesIO] = {}
        self._record_time: float = 0
        self._recoding: bool = False
        self._paused: bool = False

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
