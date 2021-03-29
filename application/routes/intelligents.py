import os
import math
import numpy as np
import scipy as sp
from scipy import stats
import tensorflow as tf
from application import app
from tensorflow.keras.layers.experimental.preprocessing import TextVectorization

def create_model(text_encoder, NUM_CLASSES):
    model = tf.keras.Sequential([
        text_encoder,
        tf.keras.layers.Embedding(
            input_dim=len(text_encoder.get_vocabulary()),
            output_dim=32,
            mask_zero=True),
        tf.keras.layers.Dropout(.2),
        tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(32)),
        tf.keras.layers.Dense(NUM_CLASSES, activation='softmax')
        ])
        
    model.compile(loss='categorical_crossentropy',
        optimizer=tf.keras.optimizers.Adam(1e-4),
        metrics=['accuracy'])

    return model

def get_initial_labelled_dataset(X_Data, Y_Data, num_samples_per_class=10):
    X, Y, X_pooled, Y_pooled = [], [], [], []
    labelled_idx = []
    counter_dict = {}

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
        Y.append(target)
        labelled_idx.append(idx)
        
    X_pooled = np.delete(X_Data, labelled_idx, axis=0)
    Y_pooled = np.delete(Y_Data, labelled_idx, axis=0)

    return np.asarray(X), np.asarray(Y), X_pooled, Y_pooled

def max_entropy_acquisition(model, X_pooled): 
    probas = model.predict(X_pooled, verbose=1)
    probas=np.array(probas, dtype=float)
    entropy_avg = sp.stats.entropy(probas, base=10, axis=1)
    query_num=round(len(X_pooled)*.1)
    uncertain_idx = entropy_avg.argsort()[-query_num:][::-1]
    return uncertain_idx, entropy_avg.mean()

def manage_data(X, Y, X_pooled, Y_pooled, idx):
    pool_mask = np.ones(len(X_pooled), dtype=bool)
    pool_mask[idx] = False
    pool_mask_2 = np.zeros(len(X_pooled), dtype=bool)
    pool_mask_2[idx] = True
    new_training = X_pooled[pool_mask_2]
    new_label = Y_pooled[pool_mask_2]
    X_pooled = X_pooled[pool_mask]
    Y_pooled = Y_pooled[pool_mask]
    X = np.concatenate([X, new_training])
    Y = np.concatenate([Y, new_label])
    return X, Y, X_pooled, Y_pooled

def extractUserData(user_data):
    NUM_CLASSES = len(user_data["tag_data"]["tags"])

    X_Data, Y_Data = [], [] #here, load the training data
    for sentence_index, sentence in enumerate(user_data["sentences"]):
        for word_index, word in enumerate(sentence.split()):
            tag_index = int(user_data["sentence_tags"][sentence_index][word_index]) #get tag index ID number from current word
            if tag_index != 0: #retrieve tag data only if there's a tag
                #print("TAG INDEX: ", tag_index)
                #tag_info = user_data["tag_data"]["tags"][tag_index]["name"] 
                X_Data.append(word)
                #one hot encode the classes
                one_hot = [0] * NUM_CLASSES
                one_hot[tag_index-1] = 1
                Y_Data.append(one_hot)

    #convert X_Data to numpy array
    return (np.array(X_Data), np.array(Y_Data))

def initialize_model(user_data):
    NUM_CLASSES = len(user_data["tag_data"]["tags"])

    X_Data, Y_Data = extractUserData(user_data)

    #set the number of values to sqrt of the length of the data
    num_samples_per_class = int(math.sqrt(len(X_Data)))

    X, Y, X_pooled, Y_pooled = get_initial_labelled_dataset(X_Data, Y_Data, num_samples_per_class)

    VOCAB_SIZE = 2000

    model = None

    #run active learning by iterating the model, manipulating the training data, and gaming the subsequent model
    for i in range(1):
        print('*' * 50)

        text_encoder = TextVectorization(max_tokens=VOCAB_SIZE)
        text_encoder.adapt(X)

        model = create_model(text_encoder, NUM_CLASSES)
        model.fit(X, Y, epochs=1, verbose=1)
        uncertain_idx, entropy_avg = max_entropy_acquisition(model, X_pooled)
        print('Average Entropy: {}'.format(entropy_avg))
        
        X, Y, X_pooled, Y_pooled = manage_data(X, Y, X_pooled, Y_pooled, uncertain_idx)
        print('Iteration Done: {}'.format(i+1))

    #return the model back
    return model

def train_existing_model(user_data):
    X_Data, Y_Data = extractUserData(user_data)

    #set the number of values to sqrt of the length of the data
    num_samples_per_class = int(math.sqrt(len(X_Data)))

    X, Y, X_pooled, Y_pooled = get_initial_labelled_dataset(X_Data, Y_Data, num_samples_per_class)

    #load the existing model
    model = load_model(user_data)

    model.fit(X, Y, epochs=3, verbose=1)

    #return the model back
    return model

def get_path(sub):
    return os.path.join(os.getcwd(), "application", "data", "ai", sub)

def load_model(user_data, model_name=None):
    if app.config["ai_model"]:
        return app.config["ai_model"]
    else: 
        model_path = get_path(model_name if model_name else user_data["model_name"])
        if os.path.exists(model_path):#load the model if it exists but is not in memory
            return tf.keras.models.load_model(model_path)
        else: 
            # return user_data # ERROR no model how did this happen!
            return initialize_model(model_name if model_name else user_data["model_name"])

def run_model(user_data, test_sentences):

    model = load_model(user_data)

    #get a prediction for every word in the selected sentences
    new_user_data = user_data
    for sentence_index in test_sentences:
        parsed_sentence = user_data["sentences"][sentence_index].split()
        for word_index, word in enumerate(parsed_sentence):
            prediction = model.predict(np.array([word]))
            predicted_tag_index = np.argmax(prediction[0]) + 1 #get the index of the maximum value
            print(predicted_tag_index)
            new_user_data["sentence_tags"][sentence_index][word_index] = int(predicted_tag_index)

    return new_user_data
        
def save_model(model, model_name):
    model = load_model(None, model_name) if not model else model
    model_path = get_path(model_name)
    if not os.path.isdir(model_path):
        os.makedirs(model_path)
    # if not model_name:
    #     user_data["model_name"] = "model"
    
    print("Model Saving started")
    model.save(model_path)
    print("Complete")
    