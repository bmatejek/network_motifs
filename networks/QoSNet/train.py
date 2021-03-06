import os
import time
import random
import keras



import numpy as np



from keras.models import Sequential
from keras.layers import Dense, Activation, BatchNormalization, Dropout
from keras.layers.advanced_activations import LeakyReLU



from network_motifs.utilities import dataIO
from network_motifs.utilities.constants import request_types_per_dataset
from network_motifs.networks.QoSNet.features import ReadFeatures



def QoSNet(parameters):
    # create simple model for this neural network
    model = Sequential()
    model.add(Dense(parameters['first-layer'], input_dim=parameters['nfeatures']))
    model.add(Activation('tanh'))
    model.add(BatchNormalization())
    model.add(Dropout(0.2))
    model.add(Dense(parameters['second-layer']))
    model.add(Activation('tanh'))
    model.add(BatchNormalization())
    model.add(Dropout(0.2))
    model.add(Dense(parameters['third-layer']))
    model.add(Activation('tanh'))
    model.add(BatchNormalization())
    model.add(Dropout(0.5))
    model.add(Dense(1))

    # compile the model
    model.compile(optimizer='adam', loss='mean_squared_error', metrics=['mae'])

    return model



def GenerateExamples(dataset_features, dataset_labels, parameters):
    # get stats about the learning process
    ndata_points = len(dataset_features)
    batch_size = parameters['batch_size']
    nfeatures = parameters['nfeatures']

    input_features = np.zeros((batch_size, nfeatures), dtype=np.float32)
    input_labels = np.zeros(batch_size, dtype=np.float32)

    indices = [iv for iv in range(ndata_points)]
    random.shuffle(indices)

    # current index in features/labels lists
    index = 0
    while True:
        for iv in range(batch_size):
            # put into format for learning
            input_features[iv,:] = dataset_features[indices[index]]
            input_labels[iv] = dataset_labels[indices[index]]

            # reset the index if overflow
            index += 1
            if index == ndata_points:
                index = 0
                random.shuffle(indices)

        # yield the created features and labels
        yield (input_features, input_labels)




def Train(dataset):
    if not os.path.exists('networks/QoSNet/architectures'):
        os.mkdir('networks/QoSNet/architectures')

    # create a new model for every request type
    for request_type in request_types_per_dataset[dataset]:
        # start statistics
        start_time = time.time()

        # read the training and validation features from disk
        training_filenames = dataIO.ReadTrainingFilenames(dataset, request_type)
        validation_filenames = dataIO.ReadValidationFilenames(dataset, request_type)

        training_features, training_labels, _ = ReadFeatures(dataset, training_filenames)
        validation_features, validation_labels, _ = ReadFeatures(dataset, validation_filenames)

        parameters = {}
        parameters['first-layer'] = 512
        parameters['second-layer'] = 256
        parameters['third-layer'] = 128
        parameters['batch_size'] = 1000
        parameters['nfeatures'] = training_features[0].size

        # create the simple model
        model = QoSNet(parameters)

        # how many example to run for each epoch
        examples_per_epoch = 20000
        batch_size = parameters['batch_size']

        model_prefix = 'networks/QoSNet/architectures/{}-request-type-{}-params-{}-{}-{}-batch-size-{}'.format(dataset, request_type, parameters['first-layer'], parameters['second-layer'], parameters['third-layer'], batch_size)

        # create the set of keras callbacks
        callbacks = []
        best_loss = keras.callbacks.ModelCheckpoint('{}-best-loss.h5'.format(model_prefix), monitor='val_loss', verbose=0, save_best_only=True, save_weights_only=True, mode='auto', period=1)
        callbacks.append(best_loss)

        json_string = model.to_json()
        open('{}.json'.format(model_prefix), 'w').write(json_string)

        model.fit_generator(
                            GenerateExamples(training_features, training_labels, parameters),
                            steps_per_epoch=examples_per_epoch // batch_size,
                            epochs=500,
                            callbacks=callbacks,
                            validation_data=GenerateExamples(validation_features, validation_labels, parameters),
                            validation_steps=examples_per_epoch // batch_size,
                            verbose=0
                            )

        # print statistics
        print ('Completed training {} {} in {:0.2f} seconds.'.format(dataset, request_type, time.time() - start_time))
