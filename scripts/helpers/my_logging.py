#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import os
import sys


def init_logging(directory, file_name):
    logger = logging.getLogger()
    logger.level = logging.INFO
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    if not os.path.isdir(directory):
        os.makedirs(directory)
    file_handler = logging.FileHandler(os.path.join(directory, file_name), mode="w")
    file_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)
    logger.addHandler(file_handler)
