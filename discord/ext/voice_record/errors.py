from __future__ import annotations


from discord.errors import DiscordException

__all__ = ("VoiceRecordException", "AlreadyRecording")


class VoiceRecordException(DiscordException):
    """Base exception class for voice record feature

    Ideally, you could catch any exceptions thrown by this voice record function to handle them.
    """

    pass


class AlreadyRecording(VoiceRecordException):
    """Returns this exception if a function that is not available is used while recording."""

    pass


class NotRecording(VoiceRecordException):
    """Returns this exception if a function that is not available is used while not recording."""

    pass
