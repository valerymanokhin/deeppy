#!/usr/bin/env python
# coding: utf-8

import os
import numpy as np
from skimage.io import imshow
from skimage import io
import deeppy as dp
from skimage.transform import rotate


def run():
    # Fetch data
     # Setup neural network
    Pool_seg_kwargs = {
        'win_shape': (2, 2),
    }

    #Y = io.MultiImage('/Users/lasse/Documents/DTU/Master/RemoteCode/deeppy/examples/img/train-labels.tif');
    #X = io.MultiImage('/Users/lasse/Documents/DTU/Master/RemoteCode/deeppy/examples/img/train-volume.tif');

    img = io.imread('/Users/lasse/Downloads/plussigns.png')

    xo = img[:,:,0]

    X = np.array((xo, rotate(xo, 180), rotate(xo, 90)))
    Y = np.array((xo, rotate(xo, 180), rotate(xo, 90)))

    n_train = 1
    n_test = 1

    imageSize = 16

    x_train = np.empty((n_train,1,1,imageSize,imageSize))
    y_train = np.zeros((n_train,imageSize*imageSize), dtype=int)

    x_test = np.empty((n_test,1,1,imageSize,imageSize))
    y_test = np.zeros((n_test,imageSize*imageSize), dtype=int)

    for im_nr in range(n_train):
        x = X[im_nr].astype(dp.float_) /255.0 - 0.5
        #x = np.arange(imageSize*imageSize, dtype=np.float)
        #x  = x.reshape((imageSize, imageSize))
        x_train[im_nr,0,0,:,:] = x[0:imageSize,0:imageSize]

        y = Y[im_nr] != 0
        y = y.astype(dp.int_)
        y_train[im_nr,:] = np.resize(y[0:imageSize,0:imageSize], (imageSize*imageSize))

    for im_nr in range(n_test):
        x = X[im_nr+n_train].astype(dp.float_) /255.0 - 0.5
        #x = np.arange(imageSize*imageSize, dtype=np.float)
        #x  = x.reshape((imageSize, imageSize))
        x_test[im_nr,0,0,:,:] = x[0:imageSize,0:imageSize]

        y = Y[im_nr+n_train] != 0
        y = y.astype(dp.int_)
        y_test[im_nr,:] = np.resize(y[0:imageSize,0:imageSize], (imageSize*imageSize))

    # Setup neural network
    nn = dp.NeuralNetwork_seg(
        layers=[
            dp.Convolutional_seg(
                n_filters=2,
                filter_shape=(3, 3),
                weights=dp.Parameter(dp.NormalFiller(sigma=2), monitor=True),
            ),
            dp.Pool_seg(),
            dp.Flatten_seg(),
            dp.FullyConnected_seg(
                n_output=3,
                weights=dp.Parameter(dp.NormalFiller(sigma=2), monitor=True),
            ),
            dp.FullyConnected_seg(
                n_output=2,
                weights=dp.Parameter(dp.NormalFiller(sigma=2), monitor=True),
            ),
            dp.MultinomialLogReg_seg(),
        ],
    )

    # Train neural network
    def valid_error():
        return nn.error(x_test, y_test)
        
    trainer = dp.StochasticGradientDescent(
        batch_size=1,
        max_epochs=5,
        learn_rule=dp.Momentum(learn_rate=0.1, momentum=0.9),
    )
    trainer.train(nn, x_train, y_train, valid_error )

    # Evaluate on test data
    #error = nn.error(x_test, y_test)
    #rint('Test error rate: %.4f' % error)


if __name__ == '__main__':
    run()