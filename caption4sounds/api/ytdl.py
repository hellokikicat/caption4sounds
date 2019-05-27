from __future__ import unicode_literals
import youtube_dl

class MyLogger(object):
    def debug(self, msg):
        pass
    def warning(self, msg):
        print(msg)
	# pass
    def error(self, msg):
        print(msg)

# def finished_hook(d):
#     if d['status'] == 'finished':
#         print(f'Done downloading {d["filename"]}, now loading and predicting ...')

def yt_audio_dl(video_id, folderpath):
    
    filename = 'nullname'
    status = 'not_started'
    def finished_hook(d):
        nonlocal filename
        nonlocal status
        if d['status'] == 'finished':
#             print(filename)
            filename = d['filename']
            status = d['status']
            print(f'Done downloading {filename}.')
        
    ydl_opts = {
        'outtmpl': folderpath+'%(id)s.%(ext)s',
        'format': 'worstaudio/worst',
#         'postprocessors': [{
#             'key': 'FFmpegExtractAudio',
#             'preferredcodec': 'mp3',
#             'preferredquality': '192',
#         }],
        'logger': MyLogger(),
        'progress_hooks': [finished_hook],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_id])
        
    print('Now loading and predicting ...')
    return(filename, status)

     
