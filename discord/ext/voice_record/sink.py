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

from abc import ABCMeta, abstractmethod
from typing import Any, TYPE_CHECKING

from io import BytesIO
from sys import platform
from subprocess import PIPE
from os import urandom, path, remove
from asyncio import create_subprocess_exec

if TYPE_CHECKING:
    pass

__all__ = ("BaseSink", "FFMPEGBaseSink")


if platform != "win32":
    CREATE_NO_WINDOW = 0
else:
    CREATE_NO_WINDOW = 0x08000000


def _create_ffmpeg_argument(
    file_type: str, /, save_file: bool = False, file_name: str = None
) -> list:
    default_arguments = [
        "ffmpeg",
        "-f",
        "s16le",
        "-ar",
        "48000",
        "-ac",
        "2",
        "-i",
        "-",
        "-f",
        file_type,
    ]
    if not save_file:
        default_arguments.append("pipe:1")
    else:
        default_arguments.append(file_name)
    return default_arguments


class BaseSink(metaclass=ABCMeta):
    """A sink is a basic object that formats and transmits recording data."""

    def __init__(self, extension: str) -> None:
        self.extension = extension

    @abstractmethod
    async def format_data(self, raw_data: bytes) -> Any:
        """|coro|

        Formats and outputs the recorded data in bytes.

        If the new object has a parent class as this object, that method must be used.

        Parameters
        -----------
        raw_data: :class:`bytes`
            Recorded raw data.
        """
        pass


class FFMPEGBaseSink(BaseSink):
    """A base sink for formatting data using ffmpeg."""

    def __init__(self, file_type: str, save_temporary_file: bool = False, **kwargs):
        super().__init__(**kwargs)

        self.file_type: str = file_type
        self.save_temporary_file: bool = save_temporary_file

    async def format_data(self, raw_data: bytes) -> Any:
        """|coro|

        Formats and outputs the recorded data in bytes.

        If the new object has a parent class as this object, that method must be used.

        Parameters
        -----------
        raw_data: :class:`bytes`
            Recorded raw data.
        """
        subprocess_argument = _create_ffmpeg_argument(self.file_type)
        temporary_file_name = None
        if self.save_temporary_file:
            temporary_file_name = f"ffmpeg-{urandom(5).hex()}.tmp"
            if path.exists(temporary_file_name):
                remove(temporary_file_name)

            subprocess_argument = _create_ffmpeg_argument(
                self.file_type, save_file=True, file_name=temporary_file_name
            )

        process = await create_subprocess_exec(
            *subprocess_argument,
            creationflags=CREATE_NO_WINDOW,
            stdout=PIPE,
            stdin=PIPE,
        )
        stdout, _stderr = await process.communicate(input=raw_data)

        if self.save_temporary_file:
            with open(temporary_file_name, "rb") as temporary_file:
                stdout = temporary_file.read()

        formatted_data = BytesIO(stdout)
        formatted_data.seek(0)
        return formatted_data
