# -*- coding: utf-8 -*-
"""my-gan-notebooks.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1b4CCHJ0N4R-eEdRxE3mkZDz86ZEGYlvG
"""

import tensorflow.keras
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Dense, LeakyReLU, Reshape, Flatten, Input
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Activation, Dropout, Conv2DTranspose
from tensorflow.compat.v1.keras.layers import BatchNormalization
import matplotlib.pyplot as plt
import cv2
import os
import numpy as np

pip install kaggle

! mkdir ~/.kaggle
! cp kaggle.json ~/.kaggle/
! chmod 600 ~/.kaggle/kaggle.json
! kaggle datasets download soumikrakshit/anime-faces

!unzip anime-faces.zip

images = []
labels = [] 
label = 0
imagePaths = os.listdir("/content/data/data")

for path in imagePaths:
        image = cv2.imread("/content/data/data/"+path) 
        if image is not None:
            image = cv2.resize(image,(64,64)) #Resizing the image, in case some are not of the same size
    
            images.append(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

import random
fig,axis=plt.subplots(5,5,figsize=(10,10))
for x in range(5):
    for y in range(5):
        axis[x,y].imshow(images[10*x+y])
        axis[x,y].axis("off")

def generator():
    epsilon=10**(-5)
    initializer=tensorflow.keras.initializers.TruncatedNormal(stddev=0.02)
    
    
    model=Sequential()
    
    
    model.add(Dense(4*4*512,activation="linear",input_shape=(100,)))
    model.add(LeakyReLU(alpha=0.2))
    model.add(Reshape((4, 4, 512)))
    
    model.add(Conv2DTranspose(512, kernel_size=[4,4], strides=[2,2], padding="same",kernel_initializer= initializer))
    model.add(BatchNormalization(momentum=0.9, epsilon=epsilon))
    model.add(LeakyReLU(alpha=0.2))

    model.add(Conv2DTranspose(256, kernel_size=[4,4], strides=[2,2], padding="same",kernel_initializer= initializer))
    model.add(BatchNormalization(momentum=0.9, epsilon=epsilon))
    model.add(LeakyReLU(alpha=0.2))

    model.add(Conv2DTranspose(128, kernel_size=[4,4], strides=[2,2], padding="same",kernel_initializer= initializer))
    model.add(BatchNormalization(momentum=0.9, epsilon=epsilon))
    model.add(LeakyReLU(alpha=0.2))

    model.add(Conv2DTranspose(64, kernel_size=[4,4], strides=[2,2], padding="same", kernel_initializer= initializer))
    model.add(BatchNormalization(momentum=0.9, epsilon=epsilon))
    model.add(LeakyReLU(alpha=0.2))

    model.add(Conv2DTranspose(3, kernel_size=[4,4], strides=[1,1], padding="same", kernel_initializer= initializer))

    
    model.add(Activation("tanh"))
    
    
    noise = Input(shape=(100,))
    img = model(noise)

    return Model(noise, img)

def discriminator():
    model=Sequential()
    
    model.add(Conv2D(128, (3,3), padding='same', input_shape=(64,64,3)))
    model.add(LeakyReLU(alpha=0.18))
    model.add(BatchNormalization())
    
    
    model.add(Conv2D(128, (3,3), padding='same'))
    model.add(LeakyReLU(alpha=0.2))
    model.add(BatchNormalization())
    model.add(MaxPooling2D(pool_size=(3,3)))
    model.add(Dropout(0.2))

    model.add(Conv2D(128, (3,3), padding='same'))
    model.add(LeakyReLU(alpha=0.2))
    model.add(BatchNormalization())
    
    
    model.add(Conv2D(128, (3,3), padding='same'))
    model.add(LeakyReLU(alpha=0.2))
    model.add(BatchNormalization())
    model.add(MaxPooling2D(pool_size=(3,3)))
    model.add(Dropout(0.3))

    model.add(Flatten())
    model.add(Dense(128))
    model.add(LeakyReLU(alpha=0.2))
    model.add(Dense(128))
    model.add(LeakyReLU(alpha=0.2))
    
    
    model.add(Dense(1, activation='sigmoid'))

    

    img = Input(shape=(64,64,3))
    validity = model(img)

    return Model(img, validity)

trainX=np.array(images)
trainX= (trainX.astype(np.float32)-127.5)/127.5
batch_size=128
half_batch=batch_size//2
disc_loss=[0,0]
generator_loss=0.00
num_epochs=13001


discriminator_=discriminator()
discriminator_.compile(loss='binary_crossentropy',optimizer=Adam(0.0002,0.5),metrics=['accuracy'])

generator_=generator()
generator_.compile(loss='binary_crossentropy', optimizer=Adam(0.0002,0.5))

complete=Sequential()
complete.add(generator_)
complete.add(discriminator_)
discriminator_.trainable=False
complete.compile(loss='binary_crossentropy', optimizer=Adam(0.0002,0.5))
losses=[]
accuracies=[]

for epoch in range(num_epochs):
    cur_idx=np.random.randint(0, trainX.shape[0], half_batch)
    imgs = trainX[cur_idx]
    noise = np.random.normal(0, 1, (half_batch, 100))
    generated = generator_.predict(noise)
    
    disc_loss_current_epoch = 0.5 * np.add(discriminator_.train_on_batch(generated, np.zeros((half_batch, 1))),discriminator_.train_on_batch(imgs, np.ones((half_batch, 1))))
    
    noise = np.random.normal(0, 1, (batch_size, 100))
    set_y = np.array([1] * batch_size)
    generator_loss_current_epoch = complete.train_on_batch(noise, set_y)
    disc_loss[0] += disc_loss_current_epoch[0]
    disc_loss[1] += disc_loss_current_epoch[1]
    generator_loss += generator_loss_current_epoch
    
    
    if epoch%50==0:
        print("Discriminator Loss: "+str(disc_loss[0]/50))
        print("Generator Loss: "+ str(generator_loss/50))
        print("Accuracy: "+str(disc_loss[1]/50)+" after epoch " +str(epoch))
        accuracies.append(disc_loss[1]/50)
        losses.append([disc_loss[0]/50,generator_loss/50])
        disc_loss=[0,0]
        generator_loss=0.00
    
    if epoch%1000==0:
        noise = np.random.normal(0, 1, (25, 100))
        generated = generator_.predict(noise)
        
        generated = 0.5*generated
        generated += 0.5

        fig, axis = plt.subplots(5,5, figsize = (10,10))

        for i in range(5):
            for j in range(5):
                axis[i,j].imshow(generated[5*i+j])
        plt.show()
        fig.savefig("generated_after_epoch_%d.png" % epoch)
        plt.close()

"""# New Section"""

xaxis=[x for x in range(0,13001,50)]
losses1=[x[0] for x in losses ]
losses2=[x[1] for x in losses]
plt.plot(xaxis,accuracies)

plt.plot(xaxis,losses1)

plt.plot(xaxis,losses2)

