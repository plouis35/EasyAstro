#!/usr/bin/python3

import numpy as np
import matplotlib.pyplot as plt
from scipy.misc import imread, imsave

image_data = imread('test.jpg').astype(np.float32)

print('Size: ', image_data.size)
print('Shape: ', image_data.shape)
print(image_data)

scaled_image = image_data / 255.

plt.imshow(scaled_image)
plt.show() 

exit()


