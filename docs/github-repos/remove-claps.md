---
comments: true
---

# Remove Audience Claps

[GitHub Repository](https://github.com/reynardo-tjhin/remove-claps)

The purpose of this small project is to remove audience claps in a classical music video. I trained multiple machine learning models to identify if a snippet of an audio is classified as a audience clap. This repository contained research methods instead of a direct solution.

## The Idea

The solution that I thought of was an interative solution. The idea was to iterate each snippet of audio across the full audio. With each snippet, determine whether the audio has audience clapping.

For instance, if we set the duration of the snippet of the audio to be 2 seconds, then a 10-second audio will have 5 snippets.
```txt
snippet     1     2     3     4     5
         +-----+-----+-----+-----+-----+
         |  |  |  |  |  |  |  |  |  |  |
duration 0  1  2  3  4  5  6  7  8  9  10
```

But what if the audience clapping starts from 0.5 to 5.5? For this small project, **I assume that there is no music being played at the start of the video**. Therefore, I can assume that the audience clap starts from 0 to 5.5. But it still does not solve audience clap audio until 5.5. I solved this issue by performing another iteration backwards.

Based on the above example, we will first iterate each 2-second audio snippet in the entire 10-second audio. We stop until we determine that there is no audience clap audio in the 2-second audio snippet.
```txt
Iteration 1 - has audience clapping
snippet     1
         +-----+
         |  |  |  |  |  |  |  |  |  |  |
duration 0  1  2  3  4  5  6  7  8  9  10

Iteration 2 - has audience clapping
snippet           2
               +-----+
         |  |  |  |  |  |  |  |  |  |  |
duration 0  1  2  3  4  5  6  7  8  9  10

Iteration 3 - has audience clapping
snippet                 3
                     +-----+
         |  |  |  |  |  |  |  |  |  |  |
duration 0  1  2  3  4  5  6  7  8  9  10

Iteration 4 - no audience clapping
snippet                       4
                           +-----+
         |  |  |  |  |  |  |  |  |  |  |
duration 0  1  2  3  4  5  6  7  8  9  10

Iteration stops/breaks
```

We found that the audience clap is somewhere in between 0 to 6 seconds. We then need to perform the backward iteration. We need to set another duration variable. Let's assume that this variable is 0.1 second. We then perform the backward iteration from the start time of the final iteration minus the variable, i.e. 6 - 0.1 = "5.9"th second.
```txt
Iteration 1 - no audience clapping
snippet                 +-------+
                        |   |   |
duration 0   ...   4.9 5.9 6.9 7.9 ...

Iteration 2 - no audience clapping
snippet                +-------+
                       |   |   |
duration 0  ...   4.8 5.8 6.8 7.8 ...

Iteration 3 - no audience clapping
snippet               +-------+
                      |   |   |
duration 0  ...  4.7 5.7 6.8 7.7 ...

We keep going...

Iteration 24 - no audience clapping
snippet          +-------+
                 |   |   |
duration 0 ...  3.6 4.6 5.6 ...

Iteration 25 - has audience clapping
snippet         +-------+
                |   |   |
duration 0 ... 3.5 4.5 5.5 ...

We stop.
```
Then, we conclude that the audience stops clapping after 5.5 seconds. Therefore, the idea is that we require two iterations to find out the duration of audience clapping.

In this project, the snippet duration is set to be 1.8 seconds. It is determined via human ear, aka my ear 🫣. Check out [remove-claps/notebooks/duration-exploration.ipynb](https://github.com/reynardo-tjhin/remove-claps/blob/main/notebooks/duration-exploration.ipynb) for further details. On the other hands, the backward iteration duration is set to be 0.05 seconds for a more balanced of performance and accuracy.

This idea is implemented in the `remove_claps` function in [remove-claps/src/remove_claps.py](https://github.com/reynardo-tjhin/remove-claps/blob/main/src/remove_claps.py).

## Machine Learning Problem

In order to determine whether a snipet of an audio has audience clapping, a machine learning model is required. Therefore, we will need a dataset, the features to train on and picking the right model.

### The Dataset

In my opinion, the dataset is the most challenging to obtain. Around 20 classical music videos from YouTube are used. Then, I manually get the duration of the audience clapping for each classical music video (you can see the data here - [remove-claps/csv/new_dataset.csv](https://github.com/reynardo-tjhin/remove-claps/blob/main/csv/new_dataset.csv)).

Afterwards, I manually created snippets of audio with 1.8 seconds of duration from the 20 YouTube videos. These audios are classified as "yes". To create a "no" dataset, I randomly select 1.8-second duration of audio from the audio that does not have any audience clapping (the same 20 YouTube videos). The number data of the "yes" class needs to be similar to the number of data of the "no" class to prevent biasedness in the model.

### The Audio Features

I learned audio processing from a YouTube series called [Audio Signal Processing for Machine Learning](https://www.youtube.com/playlist?list=PL-wATfeyAMNqIee7cH3q1bh4QJFAaeNv0). Basically, each 1.8-second audio can be characterised by numerical values. These values are computed with the help of [librosa](https://librosa.org/) library. The audio features used to train the model are

- Root-Mean-Square Energy
- Zero-Crossing Rate
- Spectral Centroid
- Spectral Bandwidth
- Spectral Flatness
- Spectral Rolloff

The mean and standard deviation of these features are then computed.

### The Model

Now, we need to create a model to determine whether a snippet of an audio has audience clapping. This problem is considered as a classification problem, hence, we need to build a classification model.

I trained a total of 11 machine learning models from [scikit-learn](https://scikit-learn.org/stable/) library.

- Support Vector Classifier
- Extra Trees Classifier
- Linear Discriminant Analysis
- Decision Trees Classifier
- K-Nearest Neighbors Classifier
- Random Forest Classifier
- Multilayer Perceptrons Classifier
- AdaBoost Classifier
- Nu-Support Classifier
- Gaussian Naive Bayes Classifier

The performance of each model is recorded in [remove-claps/src/models/train_result.csv](https://github.com/reynardo-tjhin/remove-claps/blob/main/src/models/train_result.csv). I did not perform a deep analysis of why certain models score better than others. Based on the results, I picked MLP classifier as it scored the highest in all the metrics in the test dataset.

## Afterword

This project is personal to me as it involves classical music, which is my favourite subject, and also, it is my first project related to Machine Learning/Artificial Intelligence. Moreover, as of writing this in 2026, I did this project without much help from AI/LLM which is something that I am proud of. I used LLM to help improve the writing in [remove-claps/reports/README.md](https://github.com/reynardo-tjhin/remove-claps/tree/main/reports).
