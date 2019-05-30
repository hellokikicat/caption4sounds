from __future__ import print_function
import pandas as pd
import numpy as np
import tensorflow as tf
from pydub import AudioSegment
from pathlib import Path
import vggish_input
import vggish_params
import vggish_postprocess
import vggish_slim

def audio_load(filename):
    song = AudioSegment.from_file(Path(filename))
    songwave = np.array(song.get_array_of_samples()).reshape(-1, song.channels)/ song.max_possible_amplitude
    return songwave

def load_checkpoint(checkpointfile):
    tf.reset_default_graph()
    tf.Graph().as_default()
    sess = tf.Session()
    vggish_slim.define_vggish_slim(training=False)
    vggish_slim.load_vggish_slim_checkpoint(sess, checkpointfile)
    return sess

def feature_extraction(songwave, pca_params, session):
    examples_batch = vggish_input.waveform_to_examples(songwave, vggish_params.SAMPLE_RATE)
    pproc = vggish_postprocess.Postprocessor(str(pca_params))
    features_tensor = session.graph.get_tensor_by_name(vggish_params.INPUT_TENSOR_NAME)
    embedding_tensor = session.graph.get_tensor_by_name(vggish_params.OUTPUT_TENSOR_NAME)
    [embedding_batch] = session.run([embedding_tensor],feed_dict={features_tensor: examples_batch})
    postprocessed_batch = pproc.postprocess(embedding_batch)
    return postprocessed_batch


def block(vggish_features, window, hop):
    index_window = np.arange(window)
    index_hop = np.arange(0,vggish_features.shape[0] - hop - (10 - vggish_features.shape[0]%window) - 1, hop)[:, np.newaxis]
    rolling_block = np.take(vggish_features,index_window + index_hop, axis=0)
    return rolling_block

def model_prediction(pathname, modelname, block_10s, normsize, threshold):
    model = tf.keras.models.load_model(Path(pathname)/ modelname)
    prediction = model.predict(block_10s/ normsize)
    find_label_index = np.where(prediction > threshold)
    time_index = find_label_index[0]
    predicted_label = find_label_index[1]
    top_preds = []
    for i in range(block_10s.shape[0]):
        idx = (i == time_index)
        top_preds.append((i, list(predicted_label[idx])))
    return top_preds

def prediction_label(pathname, labels_file, labels_col, preds,):
    df = pd.read_csv(Path(pathname)/ labels_file)
    series = df[labels_col]
    labels = [(x, list(series[y])) for x, y in preds]
    return labels
