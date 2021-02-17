import os
import cv2
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.model_selection import train_test_split

def train_ai():
    EPOCHS = 10
    NUM_CATEGORIES = None #set to number of tags availible ? how does this work when user creates new tags on demand ?
    TEST_SIZE = 0.4

    ########
    # create training data from JSON or CSV file or files exported from app, or other training data
    ########

    text, tags = None, None #here, load the training data

    # Split data into training and testing sets
    tags = tf.keras.utils.to_categorical(tags)
    x_train, x_test, y_train, y_test = train_test_split(np.array(text), np.array(tags), test_size=TEST_SIZE)

    # Get a compiled neural network
    # MAYBE USE RECURRENT MODEL!
    model = keras.models.Sequential()
    model.add(keras.Input(shape=(None, None, None))) #set shape to..... what now? If all sentences are different, what to do... 
    model.add(layers.Dense(128, activation="relu")) # Add a hidden layer of 128 nodes
    model.add(layers.Dropout(0.5)) #Dropout 50% of nodes
    model.add(layers.Dense(256, activation="relu")) # Add a hidden layer of 256 nodes
    model.add(layers.Dropout(0.5)) #Dropout 50% of nodes
    model.add(layers.Dense(NUM_CATEGORIES, activation="softmax")) # Add an output layer with output units for all tags
    
    model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"]) #ask adam to optimize the data. let's hope he's having a good day.
    model.fit(x_train, y_train, epochs=EPOCHS) # Fit model on training data
    model.evaluate(x_test,  y_test, verbose=2) # Evaluate neural network performance

    if not os.exists("/application/data/ai/"):
        os.makedirs("/application/data/ai/")
    model.save("/application/data/ai/model")
    # print(f"Model saved to {filename}.")