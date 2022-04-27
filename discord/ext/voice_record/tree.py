from __future__ import annotations

from typing import (
    Generic,
    TypeVar,
)

__all__ = ("VoiceTree",)

ClientT = TypeVar("ClientT", bound="Client")


class VoiceTree(Generic[ClientT]):
    """Represents a container that holds user filters for recording clients.

    Parameters
    -----------
    client: :class:`~discord.Client`
        The client instance to use for the recording client.
    """

    def __init__(self, client: ClientT):
        self.client: ClientT = client
