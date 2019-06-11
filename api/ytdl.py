""" Utilities for downloading from YouTube"""

from __future__ import unicode_literals
import youtube_dl


class MyLogger(object):
    """ Custom logger for downloading status"""

    def debug(self, msg):
        pass

    def warning(self, msg):
        print(msg)

    # pass
    def error(self, msg):
        print(msg)


def yt_audio_dl(video_id, folderpath):
    """ main function for downloading audio from YouTube
    Always downloads the smallest audio file to save bandwidth, sample rate is enough
    for prediction.

    Args:
        video_id: YouTube video id, 11 char long string
        folderpath: path to folder to download audio.
    Returns:
        path to the downloaded audio file and download status 
    """
    filename = "nullname"
    status = "not_started"

    def finished_hook(d):
        nonlocal filename
        nonlocal status
        if d["status"] == "finished":
            #             print(filename)
            filename = d["filename"]
            status = d["status"]
            print(f"Done downloading {filename}.")

    ydl_opts = {
        "outtmpl": folderpath + "%(id)s.%(ext)s",
        "format": "worstaudio/worst",
        #         'postprocessors': [{
        #             'key': 'FFmpegExtractAudio',
        #             'preferredcodec': 'mp3',
        #             'preferredquality': '192',
        #         }],
        "logger": MyLogger(),
        "progress_hooks": [finished_hook],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_id])

    print("Now loading and predicting ...")
    return (filename, status)
