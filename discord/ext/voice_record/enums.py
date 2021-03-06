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

from enum import Enum
from .sink import FFMPEGBaseSink

__all__ = ("FilterStatus", "AudioSink")


class FilterStatus(Enum):
    recording = 0
    stopped = 1
    paused = 2


class AudioSink(Enum):
    m4a = FFMPEGBaseSink(file_type="ipod", save_temporary_file=True, extension="m4a")
    mka = FFMPEGBaseSink(file_type="matroska", extension="mka")
    mkv = FFMPEGBaseSink(file_type="matroska", extension="mkv")
    mp3 = FFMPEGBaseSink(file_type="mp3", extension="mp3")
    mp4 = FFMPEGBaseSink(file_type="mp4", save_temporary_file=True, extension="mp4")
    ogg = FFMPEGBaseSink(file_type="ogg", extension="ogg")
