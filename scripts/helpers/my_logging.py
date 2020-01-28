#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import os
import sys
import time
from collections import deque, namedtuple

from scripts.helpers.funs import seconds_to_hhmmssms

LogEntry = namedtuple("LogEntry", ["message", "start_time", "logger"])
log_stack = deque()


def log_start(message, logger):
    log_stack.append(LogEntry(message, time.time(), logger))
    logger.info("({}) start {}.".format(len(log_stack), message))


def log_end(additional_message=None):
    n = len(log_stack)
    log_entry = log_stack.pop()
    log_message = "({}) end {}. time elapsed: {}{}".format(n, log_entry.message,
                                                           seconds_to_hhmmssms(time.time() - log_entry.start_time),
                                                           ". {}. ".format(
                                                               additional_message) if additional_message else ".")
    log_entry.logger.info(log_message)


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
    log_stack = deque()
