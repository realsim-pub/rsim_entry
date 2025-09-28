#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import logging
import os
from logging import handlers
from dataclasses import dataclass, asdict
import platform


LOG_FORMAT = "%(asctime)s %(levelname)s %(threadName)s [%(name)s:%(lineno)s] %(message)s"
formatter = logging.Formatter(LOG_FORMAT) #, datefmt="%H:%M:%S"

@dataclass
class TimeRotateParam:
    filename: str
    when: str   # S/M/H/D/W/midnight
    interval: int
    backupCount: int

class Logger:
    if platform.system() == "Windows":
        log_dir = os.environ['USERPROFILE']
    else:
        log_dir = os.environ['HOME']
    
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    CONFIG_OUTPUT_FILE = f"{log_dir}/th_default.log"

    @staticmethod
    def config_output_file(file_path:str) -> None:
        Logger.CONFIG_OUTPUT_FILE = file_path if file_path else Logger.CONFIG_OUTPUT_FILE

    @staticmethod
    def get_logger(name:str, log_file:str=None, level=logging.INFO, propagate:bool=False):
        """To setup as many loggers as you want"""
        logger = logging.getLogger(name)
        logger.setLevel(level)
        if logger.hasHandlers():
            return logger
        
        # std stream print
        handler = logging.StreamHandler()        
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # file stream print
        if log_file is None:
            log_file = Logger.CONFIG_OUTPUT_FILE
        filehandler = handlers.RotatingFileHandler(log_file, mode='a', maxBytes=1024*1024*1024, backupCount=20)
        filehandler.setFormatter(formatter) 
        logger.addHandler(filehandler)
        logger.propagate = propagate

        return logger
    
    @staticmethod
    def get_non_terminator_logger(name:str, log_file:str=None, level=logging.INFO, propagate:bool=False):
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        formatter = logging.Formatter("%(message)s")
        # std stream print
        handler = logging.StreamHandler()     
        handler.terminator = ""   
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # file stream print
        if log_file is None:
            log_file = Logger.CONFIG_OUTPUT_FILE
        handler = logging.FileHandler(log_file)   
        handler.terminator = ""        
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = propagate

        return logger
    
    @staticmethod
    def get_time_rotate_logger(name:str, param: TimeRotateParam, level=logging.INFO, only_msg:bool=False):
        logger = logging.getLogger(name)
        logger.setLevel(level)

        handler = handlers.TimedRotatingFileHandler(**asdict(param))

        if only_msg:
            formatter = logging.Formatter("%(message)s")

        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger
