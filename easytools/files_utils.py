#
# os & files utilities
#
import os, time, sys, configparser, threading, pathlib, re, fnmatch
from logger_utils import logger
import numpy as np
from astropy.io import fits
from astropy import units as u
from astropy.nddata import CCDData, StdDevUncertainty
import matplotlib.pyplot as plt

fit_types = ['.fit', '.fits', '.fts']
dat_types = ['.csv', '.tsv', '.dat']
txt_types = ['.lst', '.txt', '.log', '.yaml', '.yml', '.json', '.bas']
img_types = ['.jpg', '.png', '.gif']

class files_utils:

    @staticmethod
    def check_access(path: str) -> bool:
        """ 
        returns True if directory or file exists and  is readable 
        """
        return (os.access(path, os.R_OK))
    
    @staticmethod
    def get_system_info() -> str:
        """ 
        returns system (os, jupyter, python versions) information for debugging purposes
        """ 
        return ('')

    @staticmethod
    def list_files(path: str, name: str = '*') -> str:
        """ 
        returns a list of files under a path, reverse sorted by last modified time
        """ 
        return fnmatch.filter((str(i).split(os.sep)[-1] 
            for i in sorted(pathlib.Path(path).iterdir(), key = os.path.getmtime, reverse = True)), name)

    @staticmethod
    def get_file_info(path: str) -> (str, int):
        """ 
        returns :
            - FIT header (if path is a FIT file) or file contents for .dat/.txt/.csv files
            - naxis for fits files (else naxis = 0)
        """    
        if pathlib.Path(path).suffix in fit_types:       
            try:
                fit_header = CCDData.read(path, unit = u.adu).header
                return (repr(fit_header), fit_header['NAXIS'])
            except KeyError:
                return ('missing KEYS in FIT file', 0)        
            except IOError as e:
                return ("I/O error({0})".format(e.args), 0)
            except:
                return ("OS error({0})".format(sys.exc_info()[1]), 0)
                
        elif pathlib.Path(path).suffix in dat_types:
            try:
                lines = ''
                with open(path, 'r') as f:
                    for i, line in enumerate(f):
                        lines += line
                      #  if i == 20:
                       #     break
                return (lines, 0)
            except:
                return ("Not a DAT file - " + str(sys.exc_info()[1]), 0)

        elif pathlib.Path(path).suffix in txt_types:
            try:
                lines = ''
                with open(path, 'r') as f:
                    for i, line in enumerate(f):
                        lines += line
                      #  if i == 20:
                       #     break
                return (lines, 0) 
            except:
                return ("Not a TEXT file - " + str(sys.exc_info()[1]), 0)

        elif pathlib.Path(path).suffix in img_types:
            try:
                img = plt.imread(path)
                return (str(img.shape), 0)
            except:
                return ("Not an image file - " + str(sys.exc_info()[1]), 0)
                
        elif pathlib.Path(path).is_dir():
            return ("Is a directory", 0)
            
        else:
            return ("File type not supported : " + pathlib.Path(path).suffix, 0)
            
    def get_file_data(path: str = None) -> (int, np):
        """ 
        opens the path file - returns a numpy array containing image data - manages all supported image types
        """    
        fit_data = np.zeros(shape=(10, 10))    # dummy image
        naxis = 0
        
        ### FIT file 
        if pathlib.Path(path).suffix in fit_types:
            try:
                fit_data = CCDData.read(path, unit = u.adu).data.copy()
                naxis = CCDData.read(path, unit = u.adu).header['NAXIS'] 
            except:
                raise 

        ### image file
        elif pathlib.Path(path).suffix in img_types:
            try:
                fit_data = plt.imread(path)
                #logger.info('Image file format = {}'.format(str(fit_data.shape)))
            except:
                raise

        ### data file 
        elif pathlib.Path(path).suffix in dat_types:
            #logger.info('DAT file type = {}'.format(path))  
            pass
        
        ### text file 
        elif pathlib.Path(path).suffix in txt_types:
            #logger.info('TEXT file type = {}'.format(path))      
            pass

        ### not supported yet
        else:
            #logger.info('Unsupported file type = {}'.format(path))
            pass
            
        return (naxis, fit_data)
