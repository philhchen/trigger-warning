from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.layers import Embedding
import numpy as np
import os
import json

MAX_WORDS = 1000000
MAX_SEQUENCE_LENGTH = 20
TEST_SPLIT = 0.4
EMBEDDING_DIM = 50
# MODEL_DIR = '/Users/Phil/Documents/trigger-warning/'
# GLOVE_DIR = '/Users/Phil/Downloads/glove'
MODEL_DIR = '/scratch/users/philhc/trigger-warning'
GLOVE_DIR = '/scratch/users/philhc/glove'


tokenizer = Tokenizer(num_words=MAX_WORDS)

def preprocessing(filename, isJson=True):
    # Preprocess data into train and test tensors
    # Get text/scores into list of list of str and list of int
    # Returns (x_train, y_train, x_val, y_val, x_test, y_test, embeddings)
    
    # Read from file into text and scores variables
    f = open(filename)
    text = []
    scores = []
    if isJson:
        d = json.load(f)
        for idnum in d:
            scores.append(d[idnum]['mean_sentiment'])
            text.append(d[idnum]['text'].split())
    else:
        for line in f:
            values = line.split()
            words = line.split()
            scores.append(int(words[0]))
            text.append(words[1:])
    scores = np.asarray(scores)

    # Use tokenizer to pad sequences and split into train, val, test
    tokenizer.fit_on_texts(text)
    sequences = tokenizer.texts_to_sequences(text)

    word_index = tokenizer.word_index
    print('Found %s unique tokens.' % len(word_index))

    data = pad_sequences(sequences, maxlen=MAX_SEQUENCE_LENGTH)
    print('Shape of data tensor:', data.shape)
    print('Shape of scores tensor:', scores.shape)

    indices = np.arange(data.shape[0])
    np.random.shuffle(indices)
    data = data[indices]
    scores = scores[indices]
    nb_test_samples = int(TEST_SPLIT * data.shape[0])

    x_train = data[:-nb_test_samples]
    y_train = scores[:-nb_test_samples]
    x_test = data[-nb_test_samples:]
    y_test = scores[-nb_test_samples:]

    # Prepare embedding matrix from glove twitter
    embeddings_index = {}
    f = open(os.path.join(GLOVE_DIR, 'glove.twitter.27B.50d.txt'))
    for line in f:
        values = line.split()
        word = values[0]
        coefs = np.asarray(values[1:], dtype='float32')
        embeddings_index[word] = coefs
    f.close()

    print('Found %s word vectors.' % len(embeddings_index))

    embedding_matrix = np.zeros((len(word_index) + 1, EMBEDDING_DIM))
    for word, i in word_index.items():
        embedding_vector = embeddings_index.get(word)
        if embedding_vector is not None:
            embedding_matrix[i] = embedding_vector

    embedding_layer = Embedding(len(word_index) + 1, EMBEDDING_DIM, weights=[embedding_matrix], input_length=MAX_SEQUENCE_LENGTH, trainable=False)

    return (x_train, y_train, x_test, y_test, embedding_layer)

filename = os.path.join(MODEL_DIR, 'data/combined_sentiments.json')
x_train, y_train, x_test, y_test, embedding_layer = preprocessing(filename)
with open(os.path.join(MODEL_DIR, 'models/tokenizer.json'),'w') as f:
    json.dump(tokenizer.word_index, f)

from keras.models import Model
from keras.layers import Input, Dense, LSTM, Bidirectional, Dropout
from keras.layers import GlobalMaxPooling1D, Conv1D, concatenate

def buildModel(model_type='CNN', dropout=0.2):
    tweet_input = Input(shape=(MAX_SEQUENCE_LENGTH,), dtype='int32')
    embedded = embedding_layer(tweet_input)
    if model_type == 'CNN' or model_type == 'combined':
        bigram_branch = Conv1D(filters=32, kernel_size=2, activation='relu')(embedded)
        bigram_branch = GlobalMaxPooling1D()(bigram_branch)
        trigram_branch = Conv1D(filters=32, kernel_size=3, activation='relu')(embedded)
        trigram_branch = GlobalMaxPooling1D()(trigram_branch)
        fourgram_branch = Conv1D(filters=32, kernel_size=4, activation='relu')(embedded)
        fourgram_branch = GlobalMaxPooling1D()(fourgram_branch)
        if model_type == 'CNN':
            merged = concatenate([bigram_branch, trigram_branch, fourgram_branch], axis=1)
        else:
            lstm = Bidirectional(LSTM(32, activation='relu'))(embedded)
            merged = concatenate([bigram_branch, trigram_branch, fourgram_branch, lstm], axis=1)
    elif model_type == 'RNN':
        merged = Bidirectional(LSTM(64, activation='relu'))(embedded)
        
    hidden = Dense(32, activation='relu')(merged)
    hidden = Dropout(dropout)(hidden)
    output = Dense(1, activation='relu')(hidden)
    model = Model(inputs=[tweet_input], outputs=[output])
    model.summary()
    return model

model = buildModel(model_type='combined')
model.compile(optimizer='rmsprop', loss='binary_crossentropy', metrics=['mae'])

import tensorflowjs as tfjs
history = model.fit(x_train, y_train, epochs=5, batch_size=32, validation_split=0.2)
tfjs.converters.save_keras_model(model, MODEL_DIR)
model.save('model.h5')

model.load_weights('model.h5')
prediction = model.predict(x_test, batch_size=32)
print('Mean absolute error:', np.mean(np.abs(prediction - y_test)))

test = ['stupid kavanaugh and brexit what is wrong with these brits', 'what about some positivity hereee']
sequences = tokenizer.texts_to_sequences(test)
data = pad_sequences(sequences, maxlen=MAX_SEQUENCE_LENGTH)
prediction = model.predict(data)
print(prediction)
