#!/usr/bin/python3

import numpy as np
from scipy.misc import imread, imsave
import pylab as plt


image_data = imread('test.jpg').astype(np.float32)
scaled_image_data = image_data / 255.

print('Size: ', image_data.size)
print('Shape: ', image_data.shape)

   
image_slice_red =  scaled_image_data[:,:,0]
image_slice_green =  scaled_image_data[:,:,1]
image_slice_blue =  scaled_image_data[:,:,2]

print('Size: ', image_slice_red.size)
print('Shape: ', image_slice_red.shape)


plt.subplot(221)
plt.imshow(image_slice_red,cmap='gray')

plt.subplot(222)
plt.imshow(image_slice_green,cmap='gray')

plt.subplot(223)
plt.imshow(image_slice_blue,cmap='gray')  

plt.subplot(224)
plt.imshow(scaled_image_data)  

plt.show()

exit()


