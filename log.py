import globals
import logging
import logging.handlers
import paramiko
import os

def init():
    global logger

    paramiko.util.log_to_file('./data/sftp.log')
    logging.getLogger("paramiko").setLevel(logging.WARNING)

    logger = logging.getLogger('autoport')

    # Set root object's lvl as it is adjusted below in chgLevel
    logLevel = getattr(logging, globals.logLevel.upper(), None)
    if not isinstance(logLevel, int):
        logLevel = logging.INFO
    logger.setLevel(globals.logLevel)

    fh = logging.handlers.RotatingFileHandler('./data/autoport.log', maxBytes=4000000, backupCount=5)
    ch = logging.StreamHandler()

    # Set console level.  This can't be changed via the settings menu
    ch.setLevel(logging.INFO)

    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    logger.info("Initializing logLevel to %s/%s" % (globals.logLevel.upper(), logLevel))

    return logger

def chgLevel(lvl):
    logLevel = getattr(logging, lvl.upper(), None)
    if isinstance(logLevel, int) and logLevel != globals.logLevel:
        logger.setLevel(logLevel)
        globals.logLevel = lvl
        logger.info("Changing logLevel to %s/%s" % (lvl.upper(), str(logLevel)))
