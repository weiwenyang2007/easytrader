import logging
import warnings
from logging.handlers import RotatingFileHandler

def warn(*args, **kwargs):
    pass
warnings.warn = warn

def setup_custom_logger(name):
    format = '%(asctime)s %(levelname)s %(module)s %(message)s'
    formatter = logging.Formatter(fmt=format)
    logging.basicConfig(handlers=[RotatingFileHandler(filename='Z:/easytrader/logs/server.log',
                    mode='w', maxBytes=512000, backupCount=4)], level='DEBUG', format=format)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger