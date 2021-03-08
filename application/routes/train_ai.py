import os
import cv2
import json
import numpy as np
import scipy as sp
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.model_selection import train_test_split



def create_model(x_train, x_test, y_train, y_test, NUM_CATEGORIES):
    model = keras.models.Sequential()
    model.add(keras.Input(shape=(None, None, None))) #set shape to..... what now? If all sentences are different, what to do... 
    model.add(layers.Dense(256, activation="relu")) # Add a hidden layer of 256 nodes
    model.add(layers.Dropout(0.4)) #Dropout 40% of nodes
    model.add(layers.Dense(256, activation="relu")) # Add a hidden layer of 256 nodes
    model.add(layers.Dropout(0.4)) #Dropout 40% of nodes
    model.add(layers.Dense(256, activation="relu")) # Add a hidden layer of 256 nodes
    model.add(layers.Dropout(0.4)) #Dropout 40% of nodes
    model.add(layers.Dense(NUM_CATEGORIES, activation="softmax")) # Add an output layer with output units for all tags
    return model



def max_entropy_acquisition(x_test, T, num_query, model):
    proba_all = np.zeros(shape=(x_test.shape[0], 10))
    for _ in range(T):
        probas = model.predict(x_test)
        proba_all += probas
    avg_proba = np.divide(proba_all, T)
    entropy_avg = sp.stats.entropy(avg_proba, base=10, axis=1)
    uncertain_idx = entropy_avg.argsort()[-num_query:][::-1]
    return uncertain_idx, entropy_avg.mean()



def manage_data(x_train, x_test, y_train, y_test, idx):
    pool_mask = np.ones(len(x_test), dtype=bool)
    pool_mask[idx] = False
    pool_mask_2 = np.zeros(len(x_test), dtype=bool)
    pool_mask_2[idx] = True
    new_training = x_test[pool_mask_2]
    new_label = y_test[pool_mask_2]
    x_test = x_test[pool_mask]
    y_test = y_test[pool_mask]
    x_train = np.concatenate([x_train, new_training])
    y_train = np.concatenate([y_train, new_label])
    return x_train, y_train, x_test, y_test



def run_model(model, user_data, test_sentences):
    new_user_data = user_data
    for i in test_sentences:
        sentence_tags = model.predict(user_data["sentences"][i])
        new_user_data["sentence_data"]



def train_ai(user_data, test_sentences, model_path, mode=0):
    EPOCHS = 10
    TEST_SIZE = 0.4

    text, tags = [], [] #here, load the training data
    for sentence_index, sentence in enumerate(user_data["sentences"]):
        for word_index, word in enumerate(sentence.split()):
            tag_index = str(user_data["sentence_tags"][sentence_index][word_index]) #get tag index ID number from current word
            tag_info = user_data["tag_data"]["tags"][tag_index] # if int(tag_index) > 0 else "no_tag" #retrieve tag data only if there's a tag
            text.append(word)
            tags.append(tag_info)

    NUM_CATEGORIES = len(user_data["tag_data"]["tags"]) #set to number of tags

    # Split data into training and testing sets
    tags = tf.keras.utils.to_categorical(tags)
    x_train, x_test, y_train, y_test = train_test_split(np.array(text), np.array(tags), test_size=TEST_SIZE)

    model = create_model(x_train, x_test, y_train, y_test, NUM_CATEGORIES) if mode == 0 else tf.keras.models.load_model(os.path.join("/application/data/ai/", model_path))
    if mode == 2: # fully automatic AI
        return run_model(model, user_data, test_sentences)

    custom_loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False) # OLD: loss="categorical_crossentropy"
    model.compile(optimizer="adam", loss=custom_loss, metrics=["accuracy"]) # ask adam to optimize the data. let's hope he's having a good day. 
    model.fit(x_train, y_train, epochs=EPOCHS, batch_size=8, verbose=0) # Fit model on training data
    
    uncertain_idx, entropy_avg = max_entropy_acquisition(x_test, 100, 20, model)
    print('Average Entropy: {}'.format(entropy_avg))
    x_train, y_train, x_test, y_test = manage_data(x_train, y_train, x_test, y_test, uncertain_idx)

    model.evaluate(x_test,  y_test, verbose=2) # Evaluate neural network performance

    if not os.exists("/application/data/ai/"):
        os.makedirs("/application/data/ai/")
    model.save(os.path.join("/application/data/ai/", model_path))
    
    return run_model(model, user_data, test_sentences)