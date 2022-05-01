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

from discord.errors import DiscordException

__all__ = ("VoiceRecordException", "AlreadyRecording", "NotRecording")


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
