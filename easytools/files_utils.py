#
# os & files utilities
#
import os, time, sys, configparser, threading, pathlib, re, fnmatch
from logger_utils import logger
import numpy as np
from astropy.io import fits
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
        #return [str(i).split(os.sep)[-1] for i in sorted(pathlib.Path(path).iterdir(), key = os.path.getmtime, reverse = True)]
        return fnmatch.filter((str(i).split(os.sep)[-1] 
            for i in sorted(pathlib.Path(path).iterdir(), key = os.path.getmtime, reverse = True)), name)


    @staticmethod
    def get_file_info(path: str) -> str:
        """ 
        returns FIT header if path is a FIT file or 1st lines for .dat/.txt/.csv files
        """    
        if pathlib.Path(path).suffix in fit_types:       
            try:
                with fits.open(path, ignore_missing_simple=True) as hdus:
                    return (repr(hdus[0].header))
            except KeyError:
                return ('missing KEYS in FIT file')        
            except IOError as e:
                return ("I/O error({0})".format(e.args))
            except:
                return ("OS error({0})".format(sys.exc_info()[1]))
                
        elif pathlib.Path(path).suffix in dat_types:
            try:
                lines = ''
                with open(path, 'r') as f:
                    for i, line in enumerate(f):
                        lines += line
                        if i == 20:
                            break
                return lines + '\n...\n'
            except:
                return ("Not a DAT file - " + str(sys.exc_info()[1]))

        elif pathlib.Path(path).suffix in txt_types:
            try:
                lines = ''
                with open(path, 'r') as f:
                    for i, line in enumerate(f):
                        lines += line
                        if i == 20:
                            break
                return lines + '\n...\n'
            except:
                return ("Not a TEXT file - " + str(sys.exc_info()[1]))

        elif pathlib.Path(path).suffix in img_types:
            try:
                img = plt.imread(path)
                return (str(img.shape))
            except:
                return ("Not an image file - " + str(sys.exc_info()[1]))
                
        elif pathlib.Path(path).is_dir():
            return ("Is a directory - press 'change' button to change location")
            
        else:
            return ("File type not supported : " + pathlib.Path(path).suffix)
            
    def get_file_data(path: str = None) -> (int, np):
        """ 
        opens the path file - returns a numpy array containing image data - manages all supported image types
        """    
        fit_data = np.zeros(shape=(10, 10))    # dummy image
        naxis = 0
        
        ### FIT file 
        if pathlib.Path(path).suffix in fit_types:
            with fits.open(path, ignore_missing_simple=True) as hdus:
                if hdus[0].header['NAXIS'] == 1:
                    #logger.info('NAXIS = 1 --> returning spectra data')
                    fit_data = hdus[0].data.copy()
                    
                elif hdus[0].header['NAXIS'] == 2:
                    #logger.info('NAXIS = 2 --> returning image data')
                    fit_data = hdus[0].data.copy()
                else:
                    #logger.warning('NAXIS > 2 : image type not supported' + path)
                    pass

                naxis = hdus[0].header['NAXIS']

        ### image file
        elif pathlib.Path(path).suffix in img_types:
            try:
                fit_data = plt.imread(path)
                #logger.info('Image file format = {}'.format(str(fit_data.shape)))
            except:
                raise ("Error loading image file : " + str(sys.exc_info()[1]))

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
