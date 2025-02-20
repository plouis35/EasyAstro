""" EasyCombiner operates on a set of FIT images thru single line python statements

frames are first loaded into memory using the Images class methods.
then operations are applied in sequence on a single python line.

eg. : to generate a master bias image : 
master_bias = Images.from_fit(dir = "../CAPTURE/test01/", filter = "offset-*.fit") \
                    .trim('600, 600, 2700, 1400') \
                    .sigmaclip() 
                    .offset(1500 * u.adu)
                        
eg. : to reduce spectra raw frames : 
master_sciences = Images.from_fit(dir = "../CAPTURE/test01/", filter = "agdra-*.fit") \
                        .trim('600, 600, 2700, 1400' ) \
                        .reduce(master_bias, master_dark, master_flat, 'EXPTIME') \
                        .spec_align()
                  
"""
from typing import List, Tuple
import warnings, fnmatch, os
import numpy as np
from logger_utils import logger, handler
from astropy.io import fits
from astropy import units as u
from astropy.nddata import CCDData, StdDevUncertainty
from astropy.visualization import astropy_mpl_style, quantity_support
from astropy.utils.exceptions import AstropyWarning
from ccdproc import combine, subtract_bias, subtract_dark, flat_correct
from ccdproc import trim_image, Combiner, ccd_process, cosmicray_median, cosmicray_lacosmic, create_deviation
from ccdproc import ImageFileCollection, gain_correct
from astropy.stats import mad_std
import astroalign as aa
from scipy.signal import fftconvolve
#warnings.simplefilter('ignore', category=AstropyWarning)
#warnings.simplefilter('ignore', UserWarning)

class EasyCombiner(object):
    """
    maintains images set array
    max memory is used by ccdproc routines to avoid OOM exceptions when working with large set of big images
    """
    def __init__(self, images: List[CCDData], max_memory: float = 4e9):
        self._images = images
        self._memory_limit = max_memory
    """
    returns a specific image array thru its index
    """
    def __getitem__(self, i:int) -> np.ndarray:
        return self._images[i]

    """
    returns the number of frames loaded in this set
    """
    def __len__(self) -> int:
        return len(self._images)

    """
    returns the sum frame of frames loaded in this set
    """
    def sum(self) -> CCDData:
        logger.info(f'sum combine on {len(self._images)} images ...')
        return(combine(self._images,
                       method = 'sum',
                       dtype = np.float32,
                       mem_limit = self._memory_limit)
              )
   
    """
    returns the sigmaclip'ed frame of frames loaded in this set
    """
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

    """
    returns the median frame of frames loaded in this set
    """
    def median(self) -> CCDData:
        logger.info(f'median combine on {len(self._images)} images ...')
        return (combine(self._images, 
                        method = 'median', 
                        dtype = np.float32, 
                        mem_limit = self._memory_limit)
               )

    """
    trim all frames loaded in this set
    trim_region is the rectangle : x1, y1, x2, y2 
    """
    def trim(self, trim_region: str):
        if trim_region is not None:
            for i in range(0, len(self._images)):
                self._images[i] = trim_image(self._images[i][eval(trim_region)[1]:eval(trim_region)[3], eval(trim_region)[0]:eval(trim_region)[2]])

            logger.info(f'{len(self._images)} images trimmed to ({trim_region})')
        else:
            logger.info('no trimming')
        return self


    """
    trim all frames loaded in this set on an y-axis position and percentage
    """        
    def y_crop(self, y_crop: str | None):
        # y_crop contains a tuple: y_pos for relative y center, y_ratio for relative crop arround this y center
        y_center = 0.5      # default to middle
        y_ratio = 0.3       # default to 30%
    
        if y_crop is not None:
            y_center, y_ratio= eval(y_crop)

        if y_crop is not None:
            for i in range(0, len(self._images)):
                x1, x2, y1, y2 = Images.compute_crop(self._images[i], y_center, y_ratio)
                self._images[i] = trim_image(self._images[i][y1:y2, x1:x2])
            logger.info(f"{len(self._images)} science images y-cropped to {y1=}, {y2=}")
        else:
            logger.info('no y-cropping to do')
        return self
    
    """
    add a scalar to all frames loaded in this set
    """
    def offset(self, scalar):
        for i in range(0, len(self._images)):
            self._images[i] = CCDData(CCDData.add(self._images[i], scalar), header = self._images[i].header) #, unit = self._images[i].unit
            
        logger.info(f'{len(self._images)} images added by ({operand})')
        return self
    """
    substract a master bias frame to all frames loaded in this set
    """
    def bias_substract(self, frame):
        for i in range(0, len(self._images)):
            self._images[i] = subtract_bias(self._images[i], frame)
            
        logger.info(f'masterbias substracted to {len(self._images)} images')
        return self

    """
    substract a master dark frame to all frames loaded in this set
    """
    def dark_substract(self, frame, scale_exposure: bool = True, exposure = 'EXPTIME'):
        for i in range(0, len(self._images)):
            self._images[i] = subtract_dark(self._images[i], frame, scale = scale_exposure, exposure_time = exposure, exposure_unit = u.second)                
        
        logger.info(f'masterdark substracted to {len(self._images)} images')
        return self
    
    """
    divide a master flat frame to all frames loaded in this set
    """
    def flat_divide(self, frame):
        for i in range(0, len(self._images)):
            self._images[i] = flat_correct(ccd = self._images[i], flat = frame, min_value = None, norm_value = 10000 * u.adu)

        logger.info(f'masterflat divided to {len(self._images)} images')
        return self

    """
    process science frames
    masterdark frame is scaled according to science frame exposure duration
    """
    def reduce(self, master_bias, master_dark, master_flat, exposure_key = 'EXPTIME'):
        for i in range(0, len(self._images)):
            self._images[i] = ccd_process(ccd = self._images[i], 
                oscan = None, 
                gain_corrected = True, 
                trim = None, 
                error = False,
#                gain = camera_electronic_gain*u.electron/u.adu ,
#                readnoise = camera_readout_noise*u.electron,
                master_bias = master_bias,
                dark_frame = master_dark,
                master_flat = master_flat,
                exposure_key = exposure_key,
                exposure_unit = u.second,
                dark_scale = True)            

        logger.info(f'{len(self._images)} images reduced')
        return self

    """
    align a set of loaded frames - specific to stars fields (astroalign based)
    """
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

    """
    align a set of loaded frames - specific to spectra fields (fft based)
    """
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

"""
Images class implements the images loader methods

"""
class Images(EasyCombiner):
    def __init__(self, images: List[CCDData]):
        EasyCombiner.__init__(self, images)

    """
    collect and sort (according to fit header 'date-obs') file names using a wildcard filter
    """
    @classmethod
    def find_files(cls, directory: str, files_filter: str, sort_key: str = 'date-obs') -> List[str]:
        ic = ImageFileCollection(directory, glob_include = files_filter)
        ic.sort([sort_key])
        return (ic.files_filtered(include_path=True))

    """
    load a set of FIT images
    create deviation metadata from the gain & readnoise provided
    """
    @classmethod
    def from_fit(cls, dir: str, filter: str, 
                 camera_electronic_gain: float = 1.2 * u.electron / u.adu, 
                 camera_readout_noise: float =  2.2 * u.electron):
        
        images = []
        for fp in Images.find_files(directory = dir, files_filter = filter):
            #images.append(create_deviation(CCDData.read(fp, unit = u.adu),
             #                              gain = camera_electronic_gain,
              #                             readnoise = camera_readout_noise,
               #                            disregard_nan = True
                #                          ))
            images.append(CCDData.read(fp, unit = u.Unit('adu')))
            logger.info(f'image : {fp} loaded')
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

    @classmethod
    def compute_crop(cls, img:CCDData, y_center: float = 0.5, y_ratio: float = 0.3) -> tuple[float, float, float, float]:
        """
        compute array coords to crop to

        Args:
            img (CCDData): image to crop
            y_center (float, optional): relative center. Defaults to 0.5.
            y_ratio (float, optional): relative y_size. Defaults to 0.4.

        Returns:
            tuple[float, float, float, float]: x1, x2, y1, y2
        """            

        x1 = 0
        x2 = img.shape[1]
        y1 = round((img.shape[0] * y_center) - ((img.shape[0] * y_ratio) / 2))
        y2 = round((img.shape[0] * y_center) + ((img.shape[0] * y_ratio) / 2))
        return x1, x2, y1, y2


