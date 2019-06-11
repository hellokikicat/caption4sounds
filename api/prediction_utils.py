"""
Utility functions for audio loading, model loading, and making predictions
"""

import pandas as pd
import numpy as np
import tensorflow as tf

# from tensorflow.keras import layers
# classifier = tf.keras.models.load_model('models/attn_feat_02_layers-2-stage_02-after_060000batches.h5')

from pydub import AudioSegment
from pathlib import Path


def audio_load(filename):
    """ Load audio file using pydub w/ ffmpeg and returns a numpy array with sample rate
    Requires FFMPEG to be installed on system

    Args:
        filename: path to input audio file in any format that's readable by ffmpeg
    Returns:
        a 2-tuple: (numpy array of waveform, native sample rate of the audio)
    """
    song = AudioSegment.from_file(Path(filename))
    songwave = (
        np.array(song.get_array_of_samples()).reshape(-1, song.channels)
        / song.max_possible_amplitude
    )
    return songwave, song.frame_rate


def load_checkpoint(checkpointfile):
    """ Load checkpoint file for vggish

    Args:
        checkpointfile: path to tf checkpoint file of the pretrained vggish model
    Returns:
        a TF session containing restored weights of vggish
    """
    import vggish.vggish_slim

    # tf.reset_default_graph()
    tf.Graph().as_default()
    sess = tf.Session()
    vggish.vggish_slim.define_vggish_slim(training=False)
    vggish.vggish_slim.load_vggish_slim_checkpoint(sess, checkpointfile)
    return sess


def construct_classifier(model_path):
    import tensorflow as tf
    import tensorflow.keras.backend as K
    from tensorflow.keras import layers
    from tensorflow.keras.models import Model, Sequential

    num_time_steps = 10  # vggish
    emb_size = 128  # vggish
    num_labels = 527  # audioset

    hidden_layer_sizes = [1024, 1024, 1024]
    dropout_rate = 0.5

    in_out_sizes = list(zip([emb_size] + hidden_layer_sizes[:-1], hidden_layer_sizes))
    in_out_sizes

    def attn_layers(layer_size=hidden_layer_sizes[-1]):
        def attn_pool(inputs):
            #         inputs = layers.Input(shape = input_shape)
            feats = layers.Dense(layer_size, activation="linear")(inputs)
            attentions = layers.Dense(layer_size, activation="sigmoid")(inputs)
            attentions = layers.Lambda(lambda x: K.clip(x, 1e-9, 1 - 1e-9))(attentions)
            attentions = attentions / K.sum(attentions, axis=1, keepdims=True)

            outputs = K.sum(feats * attentions, axis=1)
            return outputs

        return [layers.Lambda(attn_pool)]

    transform_layers = [
        layers.Lambda(
            lambda x: K.cast(x, "float32") / 128.0 - 1.0,
            input_shape=(num_time_steps, emb_size),
        )
    ]

    linear_layers = []
    for i, o in in_out_sizes:
        linear_layers += [
            layers.Dense(o, input_shape=(num_time_steps, i)),
            layers.BatchNormalization(),
            layers.Activation("relu"),
            layers.Dropout(rate=dropout_rate),
        ]

    final_layers = [
        layers.BatchNormalization(),
        layers.Activation("relu"),
        layers.Dense(num_labels, activation="sigmoid"),
    ]

    model = Sequential(
        transform_layers + linear_layers + attn_layers(1024) + final_layers
    )
    model.summary()
    model.load_weights(weights_path)
    # classifier = tf.keras.models.load_model(model_path)
    return model


def load_classifier(model_path):
    """ Load classifier layers
    Args:
        model_path: path to keras model
    """
    return tf.keras.models.load_model(model_path)


def feature_extraction(songwave, pca_params, session, sample_rate):
    """ Applying VGGish to extract features and do post processing (PCA and discretization)

    Args:
        songwave: waveform loaded from audio file
        pca_params: pca coefficients from vggish
        session: TF session containing restored weights of VGGish
        sample_rate: sample rate of the waveform
    Returns:
        feature embedding in numpy array of shape (number of seconds of audio, 128)
    """
    import vggish.vggish_input
    import vggish.vggish_params
    import vggish.vggish_postprocess
    import vggish.vggish_slim

    examples_batch = vggish.vggish_input.waveform_to_examples(songwave, sample_rate)
    pproc = vggish.vggish_postprocess.Postprocessor(str(pca_params))
    features_tensor = session.graph.get_tensor_by_name(
        vggish.vggish_params.INPUT_TENSOR_NAME
    )
    embedding_tensor = session.graph.get_tensor_by_name(
        vggish.vggish_params.OUTPUT_TENSOR_NAME
    )
    [embedding_batch] = session.run(
        [embedding_tensor], feed_dict={features_tensor: examples_batch}
    )
    postprocessed_batch = pproc.postprocess(embedding_batch)
    return postprocessed_batch


def to_blocks(vggish_features, window, repeat, hop):
    """ Expanding a 2D array to 3D blocks by rolling window of extracted features

    Args:
        vggish_features: 2D numpy array
        window: window length, ie size of blocks
        hop: hop lengh, determines the size of new dim and how much to overlap among blocks
    Returns:
        a 3D numpy array of overlapping blocks of the original 2D array
    """
    index_window = np.tile(np.arange(window), repeat)
    # index_hop = np.arange(0,vggish_features.shape[0] - hop - (10 - vggish_features.shape[0]%window) - 1, hop)[:, np.newaxis]
    index_hop = np.arange(0, vggish_features.shape[0] - window + 1, hop)[:, np.newaxis]
    rolling_block = np.take(vggish_features, index_window + index_hop, axis=0)
    return rolling_block


def classify(model, block_10s, threshold=0.2):
    """ Forward pass of the second part of the layer, predicting probs for each label

    Args:
        pathname: path to folder of saved Keras model
        weights_name: name of saved Keras model wights
        block_10s: 3D numpy array from rolled and post processed vggish embeddings
        normsize: normalization of vggish embeddings
        threshold: probability threshold for predicting labels
    Returns:
        2D numpy array of shape ((window/hop) * num of seconds, num of labels) where
        each element is the probability of the corresponding label at corresponding time
    """
    prediction = model.predict(block_10s)
    find_label_index = np.where(prediction > threshold)
    time_index = find_label_index[0]
    predicted_label = find_label_index[1]
    top_preds = []
    for i in range(block_10s.shape[0]):
        idx = i == time_index
        top_preds.append((i, list(predicted_label[idx])))
    return top_preds


def prediction_label(pathname, labels_file, labels_col, preds):
    """ Translating numeric labels to text

    Args:
        pathname: folder path of csv file containing table of label number and texts
        labels_file: name of csv file containing table of label number and texts
        labels_col: name of column containing text labels
        preds: input list of predictions from model, indexed by time
    Returns:
        dict of predicted text labels
    """
    df = pd.read_csv(Path(pathname) / labels_file)
    series = df[labels_col]
    # labels = [(x, list(series[y])) for x, y in preds]
    labels = {x: list(series[y]) for x, y in preds}
    return labels
