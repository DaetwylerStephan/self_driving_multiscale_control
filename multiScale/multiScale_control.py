'''
multiScale_control.py
========================================
Core python script to start the multiScale control
'''

import logging
import time
import os
import sys
import importlib.util
from src.stages.rotation_stage_cmd import *

from PyQt5 import QtWidgets


def load_config(logger, configfilepath):
    '''
    Import configuration parameters, called from main function of multiScale_control at startup
    '''

    logger.info('loading configuration')

    if configfilepath != '':
        ''' Using importlib to load the config file '''
        spec = importlib.util.spec_from_file_location('module.name', configfilepath)
        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)
        logger.info(f'Configuration file loaded: {configfilepath}')
        return config
    else:
        ''' Application shutdown '''
        logger.warning('no configuration file found')
        sys.exit()






def main():
    """
    Main function
    """

    # learn more about logging: https://realpython.com/python-logging/
    # generate filename for log file
    timestr = time.strftime("%Y%m%d-%H%M%S")
    logging_filename = timestr + '.log'

    # set configuration of log file to be of log file, with the given name, all logging levels and format of reporting
    logging.basicConfig(filename='log/' + logging_filename, level=logging.INFO,
                        format='%(asctime)-8s:%(levelname)s:%(threadName)s:%(thread)d:%(module)s:%(name)s:%(message)s')

    # set up custom logger
    logger = logging.getLogger(__name__)
    logger.info('multiScale microscope started')

    #define filepath for config file and load configuration
    configfilepath = os.path.abspath('./config/multiScale_config.py')
    cfg = load_config(logger, configfilepath)

    print(cfg.stage_parameters)

    stage_id = 'usb:id:3948963323'
    rotationstage = SR2812_rotationstage(stage_id)
    rotationstage.ManualMove()
    rotationstage.closestage()


if __name__ == '__main__':
        main()