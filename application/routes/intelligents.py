import os
import math
import numpy as np
import scipy as sp
import tensorflow as tf
from sklearn.preprocessing import OneHotEncoder
from tensorflow.keras.layers.experimental.preprocessing import TextVectorization

def create_model(encoder, NUM_CLASSES):
    model = tf.keras.Sequential([
        encoder,
        tf.keras.layers.Embedding(
            input_dim=len(encoder.get_vocabulary()),
            output_dim=32,
            mask_zero=True),tf.keras.layers.Dropout(.2),
        tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(32)),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(NUM_CLASSES, activation='softmax')
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

    print(X_Data)
    
    for idx, target in enumerate(Y_Data):
        #find where the 1 is in each array of Y_Data
        index = np.where(target==1)[0][0]
        if index in counter_dict:
            if counter_dict[index] == num_samples_per_class:
                continue
            counter_dict[index] += 1
        else:
            counter_dict[index] = 1
        X.append(X_Data[idx])
        y.append(target)
        labelled_idx.append(idx)
        
   
    X_pooled = np.delete(X_Data, labelled_idx, axis=0)
    y_pooled = np.delete(Y_Data, labelled_idx)

    return np.asarray(X), np.asarray(y).reshape(-1,1), X_pooled, y_pooled


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


def initialize_model(user_data, model_path):
    X_Data, Y_Data = [], [] #here, load the training data
    for sentence_index, sentence in enumerate(user_data["sentences"]):
        for word_index, word in enumerate(sentence.split()):
            tag_index = str(user_data["sentence_tags"][sentence_index][word_index]) #get tag index ID number from current word
            tag_info = user_data["tag_data"]["tags"][tag_index]["name"] if int(tag_index) > 0 else "no_tag" #retrieve tag data only if there's a tag
            X_Data.append(word)
            Y_Data.append([tag_info])

    #convert X_Data to numpy array
    X_Data_np = np.array(X_Data)

    #encode the classes using one-hot encoding
    enc = OneHotEncoder()
    Y_Data_encoding = enc.fit_transform(np.array(Y_Data)).toarray()

    NUM_CLASSES = len(user_data["tag_data"]["tags"]) + 1

    #set the number of values to sqrt of the length of the data
    num_samples_per_class = int(math.sqrt(len(X_Data_np)))

    X, y, X_pooled, y_pooled = get_initial_labelled_dataset(X_Data_np, Y_Data_encoding, num_samples_per_class)

    VOCAB_SIZE=10000

    model = None
    #run active learning by iterating the model, manipulating the training data, and gaming the subsequent model
    for i in range(3):
        print('*'*50)

        encoder = TextVectorization(max_tokens=VOCAB_SIZE)
        encoder.adapt(X)

        model = create_model(encoder, NUM_CLASSES)

        model.fit(X, y, epochs=2, batch_size=2, verbose=1)
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
        initialize_model(user_data, model_path)

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

