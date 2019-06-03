# Caption4sounds

An accessibility tool that aims to help hearing impaired people to fully enjoy YouTube videos by providing them with captions that describe the audio track.

![alt text](https://github.com/hellokikicat/caption4sounds/blob/master/chrome_extension/caption4sounds/waveform-icon.png?raw=true)

Empowered by a Sound Event Recognition (SER) model, Caption4sounds classifies audios into 500+ categories of real-life events according to Google's [AudioSet Ontology](https://research.google.com/audioset/ontology/index.html).

The model transforms the underlying multi-label sound recognition problem to a image recognition problem by converting sound waveforms to spectrograms using Short Time Fourier Transform (STFT). This way, any convolutional model such as VGG and ResNet can be directly used.

![alt text](https://github.com/hellokikicat/caption4sounds/blob/master/.archived/spectrogram.png?raw=true)

Here, Google's [VGGish](https://ai.google/research/pubs/pub45611) model is used for preprocessing because it's pretrained on the [YouTube-8M](https://research.google.com/youtube8m/) dataset which supposingly contains a huge amount of real-world audio information and has proven to be extremely valuable for this project.


## Usage

To provide a non-intrusive way of interacting with users, a Chrome extension is provided that has the ability to directly overlay captions on top of vidoes right on YouTube's website. The extension takes care of everything: once the extension icon is clicked, it automotically sends the video ID to the prediction server and pulls the resulting caption transcript back to user's browser.

To view installation detials, please take a look at the readme in the chrome_extension subfolder.

![alt text](https://github.com/hellokikicat/caption4sounds/blob/master/.archived/pipeline.png?raw=true)

