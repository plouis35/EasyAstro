""" EasyCombiner class operates (using CCDProc and astroalign) on a set of FIT images
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
from ccdproc import trim_image, Combiner, ccd_process, cosmicray_median, create_deviation
from astropy.stats import mad_std
import astroalign as aa
from scipy.signal import fftconvolve
from logger_utils import logger, handler
warnings.simplefilter('ignore', category=AstropyWarning)
warnings.simplefilter('ignore', UserWarning)

class EasyCombiner(object):
    def __init__(self, images: List[CCDData], max_memory: float = 2e9):
        self._images = images
        self._memory_limit = max_memory
    def __getitem__(self, i:int) -> np.ndarray:
        return self._images[i]

    def __len__(self) -> int:
        return len(self._images)

    def sum(self) -> CCDData:
        logger.info(f'sum combine on {len(self._images)} images ...')
        return(combine(self._images,
                       method = 'sum',
                       dtype = np.float32,
                       mem_limit = self._memory_limit)
              )
   
    def sigmaclip(self, low_thresh: int = 5, high_thresh: int = 5) -> CCDData:
        logger.info(f'sigmaclip combine on {len(self._images)} images ...')
        return(combine(self._images,
                       method = 'average',
                       sigma_clip = True, 
                       sigma_clip_low_thresh = low_thresh, 
                       sigma_clip_high_thresh = high_thresh,
                       sigma_clip_func = np.ma.median, 
                       signma_clip_dev_func = mad_std, 
                       dtype = np.float32,
                       mem_limit = self._memory_limit)
              )

    def median(self) -> CCDData:
        logger.info(f'median combine on {len(self._images)} images ...')
        return (combine(self._images, 
                        method = 'median', 
                        dtype = np.float32, 
                        mem_limit = self._memory_limit)
               )

    def trim(self, trim_region: str):
        if trim_region is not None:
            for i in range(0, len(self._images)):
                self._images[i] = trim_image(self._images[i][eval(trim_region)[1]:eval(trim_region)[3], eval(trim_region)[0]:eval(trim_region)[2]])

            logger.info(f'{len(self._images)} images trimmed to ({trim_region})')
        else:
            logger.info('no trimming')
        return self

    def offset(self, operand):
        for i in range(0, len(self._images)):
            self._images[i] = CCDData(CCDData.add(self._images[i], operand), header = self._images[i].header) #, unit = self._images[i].unit
            
        logger.info(f'{len(self._images)} images added by ({operand})')
        return self
    
    def bias_substract(self, operand):
        for i in range(0, len(self._images)):
            self._images[i] = subtract_bias(self._images[i], operand)
            
        logger.info(f'{operand.dtype} bias substracted to {len(self._images)} images')
        return self

    def dark_substract(self, operand, scale_exposure: bool = True, exposure = 'EXPTIME'):
        for i in range(0, len(self._images)):
            self._images[i] = subtract_dark(self._images[i], operand, scale = scale_exposure, exposure_time = exposure, exposure_unit = u.second)                
        
        logger.info(f'{operand.dtype} dark substracted to {len(self._images)} images')
        return self
    
    def flat_divide(self, operand):
        for i in range(0, len(self._images)):
            self._images[i] = flat_correct(self._images[i], operand)
        
        logger.info(f'{operand.dtype} flat divided to {len(self._images)} images')
        return self

    def star_align(self, ref_image_index: int = 0):
        aligned_images = []
        #for i, img in tqdm(iterable = zip(range(len(self._images)), self._images), total=len(self._images), desc = 'aligning : '):
        for i, img in zip(range(len(self._images)), self._images):
            logger.info(f'image {i}: aligning to image ref {ref_image_index} ...')
            try: 
                reg_img, _ = aa.register(img, self._images[ref_image_index])
                aligned_images.append(CCDData(reg_img, unit = u.adu, header = img.header))

            except Exception as err:
                logger.error(f"Error {err} : aligning image {i}")
                
        logger.info('align: complete')
        return EasyCombiner(aligned_images)

    def spec_align(self, ref_image_index: int = 0):    
        ### Collect arrays and crosscorrelate all (except the first) with the first.
        logger.info('align: fftconvolve running...')
        nX, nY = self._images[ref_image_index].shape
        correlations = [fftconvolve(self._images[ref_image_index].data.astype('float32'),
                                    image[::-1, ::-1].data.astype('float32'),
                                    mode='same') 
                        for image in self._images[1:]]
    
        ### For each image determine the coordinate of maximum cross-correlation.
        logger.info('align: get max cross-correlation for every image...')
        shift_indices = [np.unravel_index(np.argmax(corr_array, axis=None), corr_array.shape) 
                         for corr_array in correlations]
        
        deltas = [(ind[0] - int(nX / 2), ind[1] - int(nY / 2)) for ind in shift_indices]
        logger.info('align: images deltas = ' + repr(deltas))
    
        ### Warn for ghost images if realignment requires shifting by more than
        ### 15% of the field size.
        x_frac = abs(max(deltas, key=lambda x: abs(x[0]))[0]) / nX
        y_frac = abs(max(deltas, key=lambda x: abs(x[1]))[1]) / nY
        t_frac = max(x_frac, y_frac)
        if t_frac > 0.15:
            logger.warning('align: shifting by {}% of the field size'.format(int(100 * t_frac)))
    
        ### Roll the images to realign them and return their median.
        logger.info('align: images realignement ...')
        realigned_images = [CCDData(np.roll(image, deltas[i], axis=(0, 1)).data.astype('float32'), unit = u.adu, header = image.header) 
                            for (i, image) in enumerate(self._images[1:])]

        ### do not forget the reference image
        realigned_images.append(CCDData(self._images[ref_image_index].data.astype('float32'), unit = u.adu, header = self._images[ref_image_index].header))
        logger.info('align: complete')
        return EasyCombiner(realigned_images)

class Images(EasyCombiner):
    def __init__(self, images: List[CCDData]):
        EasyCombiner.__init__(self, images)

    @classmethod
    def from_fit(cls, file_paths: List[str]):
        images = []
        for fp in file_paths:
            fitdata = CCDData.read(fp, unit = u.adu)
            camera_electronic_gain = 0.13 * u.electron/u.adu   # atik 420m 
            camera_readout_noise = 3.0 * u.electron     # atik 420m
            images.append(create_deviation(fitdata,
                                           gain = camera_electronic_gain,
                                           readnoise = camera_readout_noise,
                                           disregard_nan = False
                                          ))
            
        logger.info(f'set of images : {file_paths} loaded')
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


