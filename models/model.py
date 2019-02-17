from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.layers import Embedding
import numpy as np
import os
import json

MAX_WORDS = 1000000
MAX_SEQUENCE_LENGTH = 30
TEST_SPLIT = 0.4
EMBEDDING_DIM = 50
MODEL_DIR = '/Users/Phil/Documents/Treehacks/'
GLOVE_DIR = '/Users/Phil/Downloads/glove'

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
    scores = (1+scores)/2

    # Use tokenizer to pad sequences and split into train, val, test
    tokenizer = Tokenizer(num_words=MAX_WORDS)
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

# Run preprocessing
filename = os.path.join(MODEL_DIR, 'data1.json')
x_train, y_train, x_test, y_test, embedding_layer = preprocessing(filename)

# Build Model
from keras.models import Sequential
from keras.layers import Dense, LSTM, Bidirectional

model = Sequential()
model.add(embedding_layer)
model.add(Bidirectional(LSTM(32)))
model.add(Dense(1, activation='sigmoid'))

model.compile(optimizer='rmsprop', loss='binary_crossentropy', metrics=['mae'])

# Train model
import tensorflowjs as tfjs
history = model.fit(x_train, y_train, epochs=1, batch_size=32, validation_split=0.2)
tfjs.converters.save_keras_model(model, MODEL_DIR)

# Test model
prediction = model.predict(x_test)
print(np.mean(np.abs(prediction - y_test)))
