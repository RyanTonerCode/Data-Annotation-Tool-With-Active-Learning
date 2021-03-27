import os
import math
import numpy as np
import scipy as sp
import tensorflow as tf
from sklearn.preprocessing import OneHotEncoder
from tensorflow.keras.layers.experimental.preprocessing import TextVectorization

def create_model(X):
    VOCAB_SIZE=10000
    encoder = TextVectorization(max_tokens=VOCAB_SIZE)
    encoder.adapt(X)

    model = tf.keras.Sequential([
        encoder,
        tf.keras.layers.Embedding(
            input_dim=len(encoder.get_vocabulary()),
            output_dim=32,
            mask_zero=True),tf.keras.layers.Dropout(.2),
        tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(32)),
        tf.keras.layers.Dense(2, activation='softmax')
        ])
        
    model.compile(loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False),
        optimizer=tf.keras.optimizers.Adam(1e-4),
        metrics=['accuracy'])

    return model


def get_initial_labelled_dataset(X_Data, Y_Data, num_samples_per_class=10):
    X = list()
    y = list()
    X_pooled = list()
    y_pooled = list()
    labelled_idx = list()

    counter_dict = dict()
    
    for idx, target in enumerate(Y_Data):
        if target in counter_dict:
            if counter_dict[target] == num_samples_per_class:
                continue
            counter_dict[target] += 1
        else:
            counter_dict[target] = 1
        X.append(X_Data[idx])
        y.append(target)
        labelled_idx.append(idx)
        
   
    X_pooled = np.delete(np.array(X_Data), labelled_idx, axis=0)
    y_pooled = np.delete(np.array(Y_Data), labelled_idx)

    return np.asarray(X), np.asarray(y), X_pooled, y_pooled


def max_entropy_acquisition(model, X_pooled): 
    probas = model.predict(X_pooled,verbose=1)
    probas=np.array(probas,dtype = float)
    entropy_avg = sp.stats.entropy(probas, base=10, axis=1)
    query_num=round(len(X_pooled)*.1)
    uncertain_idx = entropy_avg.argsort()[-query_num:][::-1]
    return uncertain_idx, entropy_avg.mean()


def manage_data(X, y, X_pooled, y_pooled, idx):
    pool_mask = np.ones(len(X_pooled), dtype=bool)
    pool_mask[idx] = False
    pool_mask_2 = np.zeros(len(X_pooled), dtype=bool)
    pool_mask_2[idx] = True
    new_training = X_pooled[pool_mask_2]
    new_label = y_pooled[pool_mask_2]
    X_pooled = X_pooled[pool_mask]
    y_pooled = y_pooled[pool_mask]
    X = np.concatenate([X, new_training])
    y = np.concatenate([y, new_label])

    return X, y, X_pooled, y_pooled


def create_model(user_data, model_path):
    X_Data, Y_Data = np.array(), np.array() #here, load the training data
    for sentence_index, sentence in enumerate(user_data["sentences"]):
        for word_index, word in enumerate(sentence.split()):
            tag_index = str(user_data["sentence_tags"][sentence_index][word_index]) #get tag index ID number from current word
            tag_info = user_data["tag_data"]["tags"][tag_index] # if int(tag_index) > 0 else "no_tag" #retrieve tag data only if there's a tag
            np.append(X_Data, word)
            np.append(Y_Data, tag_info)

    #encode the classes using one-hot encoding
    enc = OneHotEncoder()
    Y_Data_encoding = enc.fit_transform(Y_Data).toarray()

    #set the number of values to sqrt of the length of the data
    num_samples_per_class = int(math.sqrt(len(X_Data)))

    X, y, X_pooled, y_pooled = get_initial_labelled_dataset(X_Data, Y_Data_encoding, num_samples_per_class)

    model = None
    #run active learning by iterating the model, manipulating the training data, and gaming the subsequent model
    for i in range(3):
        print('*'*50)

        model = create_model()
        model.fit(X, y, epochs=2,batch_size=128, verbose=1)
        uncertain_idx, entropy_avg = max_entropy_acquisition(X_pooled)
        print('Average Entropy: {}'.format(entropy_avg))
        
        X, y, X_pooled, y_pooled = manage_data(X, y, X_pooled, y_pooled, uncertain_idx)
        print('Iteration Done: {}'.format(i+1))

    if not os.exists("/application/data/ai/"):
        os.makedirs("/application/data/ai/")
    if not model_path:
        model_path = "model"
        user_data["model_path"] = model_path
    model.save(os.path.join("/application/data/ai/", model_path))


def run_model(model_path, user_data, test_sentences):
    if not os.path.isfile(model_path):
        create_model(user_data, model_path)

    model = tf.keras.models.load_model(os.path.join("/application/data/ai/", model_path))
        
    new_user_data = user_data
    sentence_tags = model.predict(user_data["sentences"])
    counter = 0
    for i in test_sentences:
        for j in len(user_data["sentence_tags"][i]):
            tag_index = np.where(np.array(sentence_tags[counter]) == 1)
            new_user_data["sentence_tags"][i][j] = tag_index
            counter += 1

    return new_user_data

