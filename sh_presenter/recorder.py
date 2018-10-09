import logging


class Recorder:
    def __init__(self, path):
        logging.info('Created Recorder')
        
    def __enter__(self):
        logging.info('Enter Recorder')

    def __exit__(self, exc_type, exc_value, traceback):
        logging.info('Exit Recorder')
