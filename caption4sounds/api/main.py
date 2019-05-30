import json
import prediction_utils
from fastapi import FastAPI
from ytdl import yt_audio_dl


app = FastAPI()

sess_ckpt = prediction_utils.load_checkpoint('vggish_model.ckpt')

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

@app.get("/caption/{video_id}")
def get_caption(video_id: str):
    filename, status = yt_audio_dl(video_id, 'temp_audio/')
    print('loading audio file')
    wave, sr  = prediction_utils.audio_load(filename)
    print('starting vggish')
    vggish_features = prediction_utils.feature_extraction(wave, sr, 'vggish_pca_params.npz',sess_ckpt)
    print('hopping')
    print(vggish_features.shape)
    block_10s = prediction_utils.block(vggish_features,10,2)
    print('final prediction')
    prediction = prediction_utils.model_prediction('./','unbal_1M_batchnorm_model-stage01',block_10s,256.,0.2)
    print('labeling')
    labels = prediction_utils.prediction_label('./','class_labels_indices.csv','display_name',prediction)
    print('done')

    # return json.dumps({"audio_filename": filename, "dl_status": 'finished', "results": labels})
    return {"audio_filename": filename, "dl_status": 'finished', "results": labels}
