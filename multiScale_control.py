'''
multiScale_control.py
========================================
Core python script to start the multiScale control
'''

import time
import logging

#generate filename for log file
timestr = time.strftime("%Y%m%d-%H%M%S")
logging_filename = timestr + '.log'

#set configuration of log file to be of log file, with the given name, all logging levels and format of reporting
logging.basicConfig(filename='log/'+logging_filename, level=logging.INFO, format='%(asctime)-8s:%(levelname)s:%(threadName)s:%(thread)d:%(module)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)
logger.info('multiScale microscope started')

print(timestr)

def main():
    """
    Main function
    """
    logging.info('multiScale Program started.')

if __name__ == '__main__':
        main()