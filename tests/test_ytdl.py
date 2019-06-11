""" Unit Test for ytdl.py"""

import pytest

from ..api.ytdl import *


@pytest.mark.parametrize("vid", ["bILE5BEyhdo", "qIcTM8WXFjk"])
def test_yt_audio_dl(vid):
    _, status = yt_audio_dl(vid, "api/temp_audio/")
    print(status)
    assert status == "finished"
