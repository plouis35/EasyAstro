"""
 EASYVIEWER - FIT files UI browser based on jupyter IPYWIDGETS
 UI Panels : 
         1. TOP : browse files / display selected file infos
         2. DOWN : 
                   a : image (JDA imviz)
                   b : spectra (JDA specviz)

 usage :
        viewer = EasyViewer(root_path, cuts, colormap)

 public variables/methods : 
       <TODO>
       
"""
from files_utils import *
from logger_utils import logger, handler
from ipyfilechooser import FileChooser
from IPython.display import display
import ipywidgets as widgets
import yaml
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colormaps
import matplotlib.transforms as mtransforms
from scipy import ndimage
import math
import threading
from IPython.display import display
import ipywidgets as widgets
from jdaviz import Imviz
from astropy.io import fits
from astropy import units as u
from astropy.nddata import CCDData
from specutils import Spectrum1D
from jdaviz import Specviz

class EasyViewer(object):   
    def __init__(self, root_path: str = '.', cuts: str = 'minmax', colormap : str = 'Inferno') -> None:
        """ 
        create dashboard UI and declare public variables/methods
        param : root_path optional root path to start browsing files from
        """       
        ### read configuration
        with open(__class__.__name__ + ".yaml", 'r') as cfg_file:
            try:
                self.config = yaml.safe_load(cfg_file)
            except yaml.YAMLError as except_error:
                raise (except_error)

        ### public variables
        self.root_path = root_path # or self.config['global']['root_path'] 
        self.cuts = cuts
        self.colormap = colormap
        self.selected_file = ''
        self.primary_data = np.random.randint(0, 256, size=(256, 256))
        #try:
        #    self.primary_data = np.flipud(plt.imread(self.selected_file))
        #except AppError as error:
        #    logger.error(error)
        #    raise                 
            
        self.saved_data = self.primary_data.copy()
        
        ### create all GUI components
        self.__create_logger_gui()
        
        if not files_utils.check_access(self.root_path):
            logger.error('FATAL : root directory not accessible : {} - please update config'.format(self.root_path))
            return 
            
        self.__create_browser_gui()
        self.__create_viewer_gui()

        ### monitors new files in background
        self.watch_thread = threading.Thread(target = self.__watch_files, name='EASYSPEC_watch_thread')
        self.watch_thread.start()
        logger.debug('watch thread started - tid = {}'.format(self.watch_thread))          

    def __create_logger_gui(self) -> None:
        """ 
        creates logger panel
        """    
        handler.show_logs()
        #handler.clear_logs()
        logger.setLevel(self.config['global']['log_level'])
        logger.debug('logger created')

    def __create_browser_gui(self) -> None:
        """ 
        creates browser panels
        """    
        logger.debug('Creating browser UI...')

        self.left_panel = widgets.Output(layout={'width': '40%', 'height': '300px', 'border': '1px solid grey'})
        with self.left_panel:
            try:
                ### directories browse widget
                self.dir_select = FileChooser(
                    path = self.root_path,
                    title = '', show_hidden = False, select_default = True, show_only_dirs = True,
                    layout = widgets.Layout(width = '80%')
                )
            except Exception as error:
                logger.error(f"Error reading root directory : {error = }")
                return
    
            ### file filter dialog
            self.files_filter = widgets.Text(
                description = 'Filter :',
                value = '*',
                layout = widgets.Layout(width = '80%')
            )
            
            ### file chooser dialog
            self.files_select = widgets.Select(
                description = 'File(s) :',
                layout = widgets.Layout(width = '80%', height = '230px')
            )
    
            self.browser = widgets.VBox(children = [
                #self.dir_select,
                self.files_filter,
                self.files_select
            ])

            display(self.browser)

        self.right_panel = widgets.Output(layout={'width': '60%', 'height': '300px', 'border': '1px solid grey'})
        with self.right_panel:
            ### flag refresh list of file every seconds
            self.auto_refresh = widgets.Checkbox(
                description = 'Auto refresh list',
                value = True
            )
            
            ### flag auto display new created file
            self.display_new = widgets.Checkbox(
                description = 'Auto display new file',
                value = False
            )

            ### flag multiple images displayed ?
            self.display_multiple = widgets.Checkbox(
                description = 'Multiple images displayed',
                value = False
            )

            ### file info box
            self.fit_header = widgets.Textarea(
                description = 'Infos :',
                layout = widgets.Layout(width = '90%', height = '200px'),
                disabled=True
            )
        
            ### construct & arrange widgets
            self.infos = widgets.VBox(children = [
                    self.auto_refresh,
                    self.display_new,
                    #self.display_multiple,
                    self.fit_header
            ])

            display(self.infos)

        ### display everything
        display(widgets.HBox(children=[self.left_panel, self.right_panel]))

        ### on_file_clic : display infos
        self.files_select.observe(self.display_infos, names = 'value')

    def __watch_files(self) -> None:
        """ 
        watch every sec newly created files - update list files widget contents
        """        
        if self.auto_refresh.value:
            while True:
                #logger.debug('refreshing list of files...')
                self.files_select.options = files_utils.list_files(self.dir_select.selected_path, self.files_filter.value)
                time.sleep(1)
        
            
    def __create_viewer_gui(self) -> None:
        """ 
        creates viewer panels
        """    
        logger.debug('Creating viewer UI...')   

        ### left panel : image2D on top + spectra 1D down
        self.left_panel = widgets.Output(layout={'width': '100%', 'height': '600px', 'border': '1px solid grey'})
        with self.left_panel:   
            self.imviz = Imviz()
            self.imviz.show() #height=600)

        ### right panel : all commands and correction widgets packed vertically
        self.right_panel = widgets.Output(layout = {'width': '100%', 'height': '600px', 'border': '1px solid grey'})
        with self.right_panel:
            self.specviz = Specviz()
            self.specviz.show()

        display(widgets.VBox(children=[self.left_panel, self.right_panel]))

    def display_infos(self, change: str) -> None:
        """ 
        display selected file : show info + show image/spectra
        """        
        if (self.dir_select.selected_path is not None) and (change['new'] is not None):
            self.selected_file = self.dir_select.selected_path + os.sep + change['new']
            self.fit_header.value = str(files_utils.get_file_info(self.selected_file))
            logger.info('Selected file : {}'.format(self.selected_file))
            self.naxis, self.primary_data = files_utils.get_file_data(self.selected_file)
            self.saved_data = self.primary_data.copy()
            self.display_file(self.selected_file)
        else:
            logger.info('No file selected')


    def display_file(self, path: str) -> None: 
        """ 
        show image with data in file located in path
        """
        if path == None:
            ### a directory or no image selected yet 
            logger.warning('No image selected')
        else:
            if self.primary_data is not None:
                if self.naxis == 2:
                    ### this is an image - use imviz 
                    logger.info('showing image: {}'.format(path))
                    logger.info('image size: {}'.format(self.primary_data.shape))
                    logger.info('image stats: min = {}, max = {}, std = {}, mean = {}'.format(
                            self.primary_data.min(), 
                            self.primary_data.max(), 
                            self.primary_data.std(), 
                            self.primary_data.mean()
                        )
                    )
                    self.imviz.load_data(self.primary_data, data_label=os.path.basename(path))
                    self.imviz.default_viewer.cuts = self.cuts
                    self.imviz.default_viewer.set_colormap(self.colormap);
                elif self.naxis == 1:
                    ### this is a spectrum - use specviz
                    logger.info('showing spectrum: {}'.format(path))
                    logger.info('spectrum stats: min = {}, max = {}, std = {}, mean = {}'.format(
                            self.primary_data.min(), 
                            self.primary_data.max(), 
                            self.primary_data.std(), 
                            self.primary_data.mean()
                        )
                    )
                    fitdata = Spectrum1D.read(path)  
                    _spec1d = Spectrum1D(spectral_axis = fitdata.wavelength, flux = fitdata.flux * u.adu)
                    self.specviz.load_data(_spec1d, data_label = os.path.basename(path))
            
                else:
                    ### more naxis options TO DO...
                    logger.warning('file type not displayable: {}'.format(path))
            else:
                logger.warning('no data loaded')
