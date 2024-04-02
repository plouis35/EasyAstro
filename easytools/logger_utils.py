#
# output logging messages to a dedicated jupyter cell 
# from : https://ipywidgets.readthedocs.io/en/latest/examples/Output%20Widget.html#integrating-output-widgets-with-the-logging-module
# and from https://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output
#
import ipywidgets as widgets
import logging

class CustomFormatter(logging.Formatter):
    green = "\x1b[32;20m"
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    #format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    format = "%(asctime)s  - [%(levelname)s] %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: green + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class OutputWidgetHandler(logging.Handler):
    """ Custom logging handler sending logs to an output widget """

    def __init__(self, *args, **kwargs):
        super(OutputWidgetHandler, self).__init__(*args, **kwargs)
        layout = {'width': '99.6%', 'height': '160px', 'border': '1px solid grey', 'overflow': 'auto'}
        self.out = widgets.Output(layout=layout)

    def emit(self, record):
        """ Overload of logging.Handler method """
        formatted_record = self.format(record)
        new_output = {'name': 'stdout', 'output_type': 'stream', 'text': formatted_record+'\n'}
        self.out.outputs = (new_output, ) + self.out.outputs
        
    def show_logs(self):
        """ Show the logs """
        display(self.out)
    
    def clear_logs(self):
        """ Clear the current logs """
        self.out.clear_output()

logger = logging.getLogger(__name__)
handler = OutputWidgetHandler()
handler.setFormatter(CustomFormatter())
logger.addHandler(handler)