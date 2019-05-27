from fastapi import FastAPI
from ytdl import yt_audio_dl

app = FastAPI()

# sess = load_vggish_ckpt()

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

@app.get("/caption/{video_id}")
def get_caption(video_id: str):
    
    filename, status = yt_audio_dl(video_id, 'temp_audio/')
    
#     # load audio
#     waveform = load_file(filename)
#     # go through vggish
#     vggish_features = vggish_forward(waveform, sess)
#     # hop batching
#     vggish_batch = block(vggish_features)
#     # last layers
#     preds = keras_convs(vggish_batch)
    
    return {"audio_filename": filename, "dl_status": 'finished'}