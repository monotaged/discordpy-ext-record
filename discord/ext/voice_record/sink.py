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
from typing import Any, Dict, List, Optional, TYPE_CHECKING, Union, overload

if TYPE_CHECKING:
    from io import BytesIO

__all__ = ("BaseSink",)


class BaseSink(metaclass=ABCMeta):
    """A sink is a basic object that formats and transmits recording data."""

    @abstractmethod
    async def format_data(self, raw_data: BytesIO) -> Any:
        """|coro|

        Formats and outputs the recorded data in bytes.

        If the new object has a parent class as this object, that method must be used.

        Parameters
        -----------
        raw_data: :class:`io.BytesIO`
            Recorded raw data.
        """
        pass



