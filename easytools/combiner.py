""" Combiner class operates (using CCDProc and astroalign) on a set of FIT images
"""
from typing import List, Tuple
import warnings, fnmatch, os
import numpy as np
from astropy.io import fits
from astropy import units as u
from astropy.nddata import CCDData, StdDevUncertainty
from astropy.visualization import astropy_mpl_style, quantity_support
from astropy.utils.exceptions import AstropyWarning
from ccdproc import combine, subtract_bias, subtract_dark, flat_correct
from ccdproc import trim_image, Combiner, ccd_process, cosmicray_median
import astroalign as aa
from scipy.signal import fftconvolve
from tqdm.auto import tqdm
from logger_utils import logger, handler

class Combiner(object):
    def __init__(self, images: List[np.ndarray]):
        self._images = images
        warnings.simplefilter('ignore', category=AstropyWarning)
        warnings.simplefilter('ignore', UserWarning)
        quantity_support()

    def __getitem__(self, i) -> np.ndarray:
        return self._images[i]

    def __len__(self) -> int:
        return len(self._images)

    def sum(self) -> np.ndarray:
        return np.sum(self._images, axis=0)

    def mean(self) -> float:
        return np.mean(self._images, axis=0)

    def median(self) -> np.ndarray:
        return np.median(self._images, axis=0)

    def trim(self, trim_region: str):
        if trim_region is not None:
            logger.info(f'trimming to ({trim_region}) {len(self._images)} images ...')
            if isinstance(trim_region, Combiner):
                raise NotImplemented("Combiner")
            for i in range(0, len(self._images)):
                self._images[i] = self._images[i][eval(trim_region)[1]:eval(trim_region)[3], eval(trim_region)[0]:eval(trim_region)[2]]  
        else:
            logger.info('no trimming')
        return self
    
    def addition(self, operand):
        logger.info(f'{operand.dtype} adding to {len(self._images)} images ...')
        if isinstance(operand, Combiner):
            raise NotImplemented("Combiner")
        elif isinstance(operand, np.ndarray):
            if operand.dtype != self._images[0].dtype:
                raise Exception("Incompatible dtype")
            if operand.shape != self._images[0].shape:
                raise Exception("Incompatible shapes")
            for i in range(0, len(self._images)):
                self._images[i] = self._images[i] + operand
        return self

    def substract(self, operand):
        logger.info(f'{operand.dtype} substracting to {len(self._images)} images ...')
        if isinstance(operand, Combiner):
            raise NotImplemented("Combiner")
        elif isinstance(operand, np.ndarray):
            if operand.dtype != self._images[0].dtype:
                raise Exception("Incompatible dtype")
            if operand.shape != self._images[0].shape:
                raise Exception("Incompatible shapes")
            for i in range(0, len(self._images)):
                self._images[i] = self._images[i] - operand
        return self

    def multiply(self, operand):
        logger.info(f'{operand.dtype} multiplying to {len(self._images)} images ...')
        if isinstance(operand, Combiner):
            raise NotImplemented("Combiner")
        elif isinstance(operand, np.ndarray):
            if operand.dtype != self._images[0].dtype:
                raise Exception("Incompatible dtype")
            if operand.shape != self._images[0].shape:
                raise Exception("Incompatible shapes")
            for i in range(0, len(self._images)):
                self._images[i] = np.multiply(self._images[i], operand)

        elif np.issctype(type(operand)):
            for i in range(0, len(self._images)):
                self._images[i] = self._images[i] * operand
        else:
            raise Exception("Incompatible type")
        return self

    def divide(self, operand):
        logger.info(f'{operand.dtype} dividing {len(self._images)} images ...')
        if isinstance(operand, Combiner):
            raise NotImplemented("Combiner")
        elif isinstance(operand, np.ndarray):
            if operand.dtype != self._images[0].dtype:
                raise Exception("Incompatible dtype")
            if operand.shape != self._images[0].shape:
                raise Exception("Incompatible shapes")
            for i in range(0, len(self._images)):
                self._images[i] = np.divide(self._images[i], operand)

        elif np.issctype(type(operand)):
            for i in range(0, len(self._images)):
                self._images[i] = self._images[i] / operand

        else:
            raise Exception("Incompatible type")
        return self

    def align(self, ref_image_index: int = 0) -> Combiner:
        aligned_images = []
        #for i, img in tqdm(iterable = zip(range(len(self._images)), self._images), total=len(self._images), desc = 'aligning : '):
        for i, img in zip(range(len(self._images)), self._images):
            logger.info(f'Image {i} aligning to image ref {ref_image_index}')
            try: 
                reg_img, _ = aa.register(img, self._images[ref_image_index])
                aligned_images.append(reg_img)

            except Exception as err:
                logger.error(f"Error {err} : aligning image {i}")
                
        logger.info('align complete')
        return Combiner(aligned_images)

    def align_fft(self, ref_image_index: int = 0) -> Combiner:    
        ### Collect arrays and crosscorrelate all (except the first) with the first.
        logger.info('align : fftconvolve running...')
        nX, nY = self._images[ref_image_index].shape
        correlations = [fftconvolve(self._images[ref_image_index], image[::-1, ::-1], mode='same') 
                        for image in self._images[1:]]
    
        ### For each image determine the coordinate of maximum cross-correlation.
        logger.info('align : get max cross-correlation for every image...')
        shift_indices = [np.unravel_index(np.argmax(corr_array, axis=None), corr_array.shape) 
                         for corr_array in correlations]
        
        deltas = [(ind[0] - int(nX / 2), ind[1] - int(nY / 2)) for ind in shift_indices]
        logger.info('images deltas = ' + repr(deltas))
    
        ### Warn for ghost images if realignment requires shifting by more than
        ### 15% of the field size.
        x_frac = abs(max(deltas, key=lambda x: abs(x[0]))[0]) / nX
        y_frac = abs(max(deltas, key=lambda x: abs(x[1]))[1]) / nY
        t_frac = max(x_frac, y_frac)
        if t_frac > 0.15:
            logger.warning('shifting by {}% of the field size'.format(int(100 * t_frac)))
    
        ### Roll the images to realign them and return their median.
        logger.info('images realignement ...')
        realigned_images = [np.roll(image, deltas[i], axis=(0, 1))
                            for (i, image) in enumerate(self._images[1:])]

        ### do noy forget reference image
        realigned_images.append(self._images[ref_image_index])
        logger.info('align complete')
        return Combiner(realigned_images)


class Images(Combiner):
    def __init__(self, images: List[np.ndarray]):
        Combiner.__init__(self, images)

    @classmethod
    def from_fit(cls, file_paths: List[str]):
        images = []
        for fp in file_paths:
            fitdata = CCDData.read(fp, unit = u.adu)
            images.append(fitdata.data.astype(np.float32))
            
        logger.info(f'{file_paths} loaded')
        return cls(images)

    @classmethod
    def from_rgb(cls, file_paths: List[str]):
        images = []
        ### TODO ...
        return cls(images)

    @classmethod
    def from_png(cls, file_paths: List[str]):
        images = []
        ### TODO ...
        return cls(images)

    @classmethod
    def from_jpg(cls, file_paths: List[str]):
        images = []
        ### TODO ...
        return cls(images)

    @classmethod
    def from_tiff(cls, file_paths: List[str]):
        images = []
        ### TODO ...
        return cls(images)


