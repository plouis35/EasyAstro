"""
 EASYSPEC Viewer - UI based on jupyter IPYWIDGETS
 UI Panels : 
         1. TOP : browse files / display selected file header
         2. DOWN : 
                   left : image / spectra
                   right : control widgets

 usage :
        es = EasySpec('<root directory>')

 public variables/methods : 
        es.selected_file: str              -> current file selected
        es.img_data: numpy array dim2      -> current image 
        es.spc_data: numpy array dim1      -> current spectra 
        es.show_img() -> None              -> refresh image
        es.show_spc() -> None              -> refresh spectra

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

class EasySpec(object):   
    def __init__(self, root_path: str = None) -> None:
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
        self.root_path = root_path or self.config['global']['root_path']           
        self.selected_file = 'logo_sar.png'
        #self.primary_data = np.random.randint(0, 256, size=(256, 256))
        try:
            self.primary_data = np.flipud(plt.imread(self.selected_file))
        except AppError as error:
            logger.error(error)
            raise                 
            
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
                self.dir_select,
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
                description = 'Auto display newly created file',
                value = False
            )
            
            ### wd_fit_header
            self.fit_header = widgets.Textarea(
                description = 'Infos :',
                layout = widgets.Layout(width = '90%', height = '200px'),
                disabled=True
            )
        
            ### construct & arrange widgets
            self.infos = widgets.VBox(children = [
                    self.auto_refresh,
                    self.display_new,
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
        self.left_panel = widgets.Output(layout={'width': '70%', 'height': '600px', 'border': '1px solid grey'})
        with self.left_panel:        
            with plt.ioff():
                self.fig_img, self.ax_img = plt.subplots(1, 1, constrained_layout=True, figsize=(9, 5.5), frameon=False)
            
            ### define toolbar, grid, colors...
            self.fig_img.canvas.toolbar_position = 'right'
            self.fig_img.canvas.header_visible = False
            self.fig_img.canvas.footer_visible = True
            self.fig_img.canvas.resizable = True
            self.fig_img.canvas.capture_scroll = True
            self.fig_img.canvas.toolbar_visible = True

            ### show image 2D
            self.ax_img.axis('off')
            self.ax_img.set_yscale('linear')
            self.img = self.ax_img.imshow(
                self.primary_data, 
                origin = 'lower', 
                vmin = self.primary_data.min(), 
                vmax = self.primary_data.max(), 
                interpolation='none',
                aspect = 'equal',
                cmap = 'magma'
            )
            
            def format_coord(x,y):
                return "x={:.0f}, y={:.0f} ->".format(x,y)
                
            self.ax_img.format_coord=format_coord

            __color_bar = self.fig_img.colorbar(self.img, ax = self.ax_img, location='left')

            '''
            ### plot spectra 1D
            self.x = [1, 2, 3, 4, 5]
            self.y = [2, 4, 6, 8, 10]
            self.ax_spc.set_xlabel('Pixels')
            self.ax_spc.set_ylabel('ADU')
            self.ax_spc.set_facecolor(color='xkcd:black')
            self.ax_spc.grid(True)    
            self.plt_spc = self.ax_spc.plot(self.x, self.y)
            '''
            display(self.fig_img.canvas)

        ### right panel : all commands and correction widgets packed vertically
        self.right_panel = widgets.Output(layout = {'width': '30%', 'height': '600px', 'border': '1px solid grey'})
        with self.right_panel:
            ### config menu buttons (apply, reset, load and save)
            self.cmd_apply = widgets.Button(description = 'Apply', tooltip='Apply all changes', layout={'width': '80px'})
            self.cmd_apply.on_click(self.apply_all_changes)
    
            self.cmd_reset = widgets.Button(description = 'Reset', tooltip='Undo all changes', layout={'width': '80px'})
            self.cmd_reset.on_click(self.reset_all_changes)
    
            self.cmd_load = widgets.Button(description = 'Load', tooltip='Load a configuration', layout={'width': '80px'})
            self.cmd_load.on_click(self.load_config)
    
            self.cmd_save = widgets.Button(description = 'Save', tooltip='Save a configuration', layout={'width': '80px'})
            self.cmd_save.on_click(self.save_config)

            ### pack config menu
            self.cmd_cfg = widgets.HBox(children=[
                self.cmd_apply, 
                self.cmd_reset, 
                self.cmd_load, 
                self.cmd_save
            ])

            ### image display control (levels slider, min/max, color map)
            self.min_bound = widgets.IntText(value = int(self.config['viewer']['domain_low']),description='min:',layout={'width': '180px'})
            self.max_bound = widgets.IntText(value = int(self.config['viewer']['domain_high']),description='max:',layout={'width': '180px'})
    
            #self.cut_levels = widgets.IntRangeSlider(value=[self.primary_data.min(), self.primary_data.max()], 
            self.cut_levels = widgets.IntRangeSlider(value = [int(self.config['viewer']['domain_low']), int(self.config['viewer']['domain_high'])], 
                min = int(self.config['viewer']['domain_low']), 
                max = int(self.config['viewer']['domain_high']), 
                step = 10,description = 'levels:',
                readout_format = 'd',
                layout={'width': '350px'}
            )

            self.cmap = widgets.Dropdown(options=list(colormaps),
                value = self.config["viewer"]["color_map"],
                description='color map:')

            ### histogram display
            self.histo = widgets.Output()
            with self.histo:
                with plt.ioff():
                    self.fig_histo, self.ax_histo = plt.subplots(constrained_layout = True, figsize=(3, 2), frameon = False)
                    
                #self.fig_histo.set_facecolor('xkcd:dark grey')
                self.fig_histo.canvas.header_visible = False
                self.fig_histo.canvas.footer_visible = False
                self.fig_histo.canvas.resizable = False
                self.fig_histo.canvas.capture_scroll = True
                self.fig_histo.canvas.toolbar_visible = False
                self.ax_histo.set_facecolor('xkcd:black')
                self.display_histo()

            ### pack image display widgets
            self.cmd_img = widgets.VBox(children=[
                self.cut_levels,
                widgets.HBox(children=[
                    self.min_bound,
                    self.max_bound
                ]), 
                self.cmap, 
                self.histo
            ])

            ### link min/max values to level slider &nd level_slider to histogram bars
            l1 = widgets.link((self.cut_levels, 'min'), (self.min_bound, 'value'))
            l2 = widgets.link((self.cut_levels, 'max'), (self.max_bound, 'value'))
            self.cut_levels.observe(self.histo_update, names='value')
                
            ### geometry correction 
            self.crop = widgets.Text(value = '', description = 'crop (x1,y1,x2,y2) : ')
            self.rotate = widgets.Text(value = '', description = 'rotate (deg): ')
            self.skew = widgets.Text(value = '', description = 'skew (x,y): ')
                        
            ### pack geometry widgets
            self.cmd_geometry = widgets.VBox(children=[self.crop, self.rotate, self.skew])
                            
            ### pack all
            self.cmd = widgets.VBox(children=[
                    self.cmd_cfg,
                    widgets.Accordion(children=[
                        self.cmd_img,
                        self.cmd_geometry,
                    ], titles = (
                        'Display',
                        'Geometry'
                        ),
                    layout = widgets.Layout(width = '400px', height = '560px')
                ) 
            ])
            
            display(self.cmd)

        display(widgets.HBox(children=[self.left_panel, self.right_panel]))

    def display_infos(self, change: str) -> None:
        """ 
        display selected file : show info + show image/spectra
        """        
        if (self.dir_select.selected_path is not None) and (change['new'] is not None):
            self.selected_file = self.dir_select.selected_path + os.sep + change['new']
            self.fit_header.value = str(files_utils.get_file_info(self.selected_file))
            logger.info('Selected file : {}'.format(self.selected_file))
            self.primary_data = files_utils.get_file_data(self.selected_file)
            self.saved_data = self.primary_data.copy()
            #self.apply_display_changes(self.selected_file)
        else:
            logger.info('No file selected')

    def histo_update(self, change):
        self.lower_limit_line.set_xdata([change['new'][0], change['new'][0]])
        self.upper_limit_line.set_xdata([change['new'][1], change['new'][1]])
        self.fig_histo.canvas.draw_idle()

    
    def display_histo(self) -> None:
        """ 
        show histogram 
        """        
        try:
            self.ax_histo.clear()
            self.lower_limit_line = self.ax_histo.axvline(self.cut_levels.value[0], color = 'r')
            self.upper_limit_line = self.ax_histo.axvline(self.cut_levels.value[1], color = 'r')
            self.ax_histo.set_yscale('log');
            self.ax_histo.grid(False) ;

            self.ax_histo.hist(self.primary_data.flatten(), 
                bins=64,
                range=[self.primary_data.min(), self.primary_data.max()], 
                #align='mid'
            )
            self.plt_histo = plt.show(self.fig_histo)

        except:
            logger.error("display histo error : ({0})".format(sys.exc_info()[1]))
            pass


    def apply_all_changes(self, b: widgets) -> None:
        logger.info('applying all changes...')
        self.apply_geometry_changes()
        self.apply_display_changes(self.selected_file)

    def reset_all_changes(self, b: widgets):
        logger.info('resetting image...')
        
        ### reset current transform actions
        mtransforms.Affine2D().clear()
        transform_data = self.ax_img.transData
        self.img.set_transform(transform_data)

        ### restore saved image
        self.primary_data = self.saved_data.copy()
        self.apply_display_changes(self.selected_file)
        
    def load_config(self, b: widgets):
        logger.warning('sorry, not yet implemented')

    def save_config(self, b: widgets):
        logger.warning('sorry, not yet implemented')


    def apply_display_changes(self, path: str) -> None: 
        """ 
        show image with data in file located in path
        """
        if path == None:
            ### a directory or no image selected yet 
            logger.warning('No image selected')
        else:
            #self.primary_data = files_utils.get_file_data(path)

            if self.primary_data is not None:
                logger.info('showing image : {}'.format(path))
                logger.info('image size : {}'.format(self.primary_data.shape))
                logger.info('image stats : min = {}, max = {}, std = {}, mean = {}'.format(
                        self.primary_data.min(), 
                        self.primary_data.max(), 
                        self.primary_data.std(), 
                        self.primary_data.mean()
                    )
                )
    
                self.img.norm.vmin = self.cut_levels.value[0]
                self.img.norm.vmax = self.cut_levels.value[1]
                self.ax_img.set_title(self.selected_file.split(os.sep)[-1])
                #self.fig_img.suptitle(self.selected_file.split(os.sep)[-1])
                self.img.set_cmap(self.cmap.value)
                new_extent = [0,  self.primary_data.shape[1], 0,  self.primary_data.shape[0]]
                self.img.set_extent (new_extent)
                self.img.set_data(self.primary_data)
                self.fig_img.canvas.draw_idle()
                self.display_histo()


    def apply_geometry_changes(self) -> None:
        """
        update image np array with geometry transformations defined by widgets contents
        """
        logger.info('start applying transformation...')

        mtransforms.Affine2D().clear()
        transform_data = self.ax_img.transData
        self.img.set_transform(transform_data)
        self.primary_data = self.saved_data.copy()
        
        if self.rotate.value != '':
            new_array = self.primary_data.copy()
            self.primary_data = ndimage.rotate(new_array, eval(self.rotate.value), reshape=False)
            logger.info('rotation done')
            new_array = None
            
        if self.skew.value != '':
            transform_actions = mtransforms.Affine2D().skew_deg(eval(self.skew.value)[0], eval(self.skew.value)[1])
            transform_data = transform_actions + self.ax_img.transData
            self.img.set_transform(transform_data)
            logger.info('skew done')

        if self.crop.value != '':
            self.primary_data = self.primary_data[eval(self.crop.value)[1]:eval(self.crop.value)[3], eval(self.crop.value)[0]:eval(self.crop.value)[2]]
            logger.info('crop done')

        self.apply_display_changes(self.selected_file)

       
    def display_plot(self, path: str) -> None:    
        """ 
        update plot with data contained in path
        manage file types (FIT, DAT, ...)
        """ 
        logger.info('display plot : {}'.format(path))

