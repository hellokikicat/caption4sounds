""" Definition for API endpoints"""

import json
from fastapi import FastAPI
from ytdl import yt_audio_dl
import tensorflow as tf
from tensorflow.keras import layers
import prediction_utils

# initializing fastapi
app = FastAPI()
classifier = prediction_utils.construct_classifier("models/deployed_weights.h5")

# loading vggish
sess_ckpt = prediction_utils.load_checkpoint("models/vggish_model.ckpt")


@app.get("/")
def read_root():
    """ A dummy end point for the index to test if server is alive"""
    return {"Hello": "The server is alive!"}


@app.get("/caption/{video_id}")
def get_caption(video_id: str):
    """ End point for caption requests

    Args:
        video_id: 11 character long string from YouTube videos
    Returns:
        dict containing audio file name, download status, and predicted caption transcript
    """
    classifier = prediction_utils.load_classifier(
        "models/attn_feat_02_layers-2-stage_02-after_060000batches.h5"
    )

    filename, status = yt_audio_dl(video_id, "temp_audio/")
    print("loading audio file")
    wave, sr = prediction_utils.audio_load(filename)
    print("starting vggish")
    vggish_features = prediction_utils.feature_extraction(
        wave, "models/vggish_pca_params.npz", sess_ckpt, sr
    )
    print("hopping")
    print(vggish_features.shape)
    block_10s = prediction_utils.to_blocks(vggish_features, 5, 2, 2)

    prediction = prediction_utils.classify(classifier, block_10s, 0.2)
    print("labeling")
    labels = prediction_utils.prediction_label(
        "./", "class_labels_indices.csv", "display_name", prediction
    )
    print("done")

    # return json.dumps({"audio_filename": filename, "dl_status": 'finished', "results": labels})
    return {"audio_filename": filename, "dl_status": "finished", "results": labels}
