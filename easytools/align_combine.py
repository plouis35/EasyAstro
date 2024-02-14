"""
2D image  aligment procedure using FFT
from https://github.com/bandang0/astro_reduce/blob/master/cosmetic.py
"""

from os.path import basename

import click
import numpy as np
from astropy.io import fits
from scipy.signal import fftconvolve
import logging
logger = logging.getLogger(__name__)

def align_and_combine(infiles: list[str], operation) -> np:
    '''Read fits data from list of files, return aligned and operation(sum, median, etc...) version.
    '''
    if len(infiles) == 1:
        return fits.getdata(infiles[0])

    # Collect arrays and crosscorrelate all (except the first) with the first.
    logger.info('fftconvolve running...')
    images = [fits.getdata(_).astype(np.float32) for _ in infiles]
    nX, nY = images[0].shape
    correlations = [fftconvolve(images[0], image[::-1, ::-1], mode='same') 
                    for image in images[1:]]

    # For each image determine the coordinate of maximum cross-correlation.
    shift_indices = [np.unravel_index(np.argmax(corr_array, axis=None), corr_array.shape) 
                     for corr_array in correlations]
    
    deltas = [(ind[0] - int(nX / 2), ind[1] - int(nY / 2)) 
              for ind in shift_indices]
    logger.info('images deltas = ' + repr(deltas))

    # Warn for ghost images if realignment requires shifting by more than
    # 15% of the field size.
    x_frac = abs(max(deltas, key=lambda x: abs(x[0]))[0]) / nX
    y_frac = abs(max(deltas, key=lambda x: abs(x[1]))[1]) / nY
    t_frac = max(x_frac, y_frac)
    if t_frac > 0.15:
        bits = basename(infiles[0]).split('_')
        logger.warning('In {}:{}:{}, shifting by {}% of the field size'.format(bits[0], bits[1], bits[2], int(100 * t_frac)))

    # Roll the images to realign them and return their median.
    logger.info('images alignement running...')
    realigned_images = [np.roll(image, deltas[i], axis=(0, 1))
                        for (i, image) in enumerate(images[1:])]
    
    realigned_images.append(images[0])
    logger.info('{} Combine operation running...'.format(repr(operation)))
    final_image = operation(realigned_images, axis=0)
    
    return final_image
