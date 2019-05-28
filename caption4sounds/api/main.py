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
    wavefor = audio_load('temp_audio/', filename)
    sess_ckpt = prediction_utils.load_checkpoint('vggish_model.ckpt')
    vggish_features = prediction_utils.feature_extraction(wave,'vggish_pca_params.npz',sess_ckpt)
    block_10s = prediction_utils.block(vggish_features,10,2)
    prediction = prediction_utils.model_prediction('temp_audio/','baseline_model',block_10s,256.,0.2)
    labels = prediction_utils.prediction_label('temp_audio/','class_labels_indices.csv','display_name',prediction)

    return {"audio_filename": filename, "dl_status": 'finished', "results": labels}
