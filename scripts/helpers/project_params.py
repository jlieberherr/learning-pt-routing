#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Some project parameters."""
import os
from os.path import join

OUTPUT = "output"  # name of folder with temporary output.
OUTPUT_FOLDER = join(os.getcwd(), OUTPUT)  # path of the folder with temporary output.
RESOURCES = "resources"
RESOURCES_FOLDER = join(os.getcwd(), RESOURCES)  # path of the folder with resources data.
LOG_NAME = "log.log"  # name of the log file.

# tests
TESTS = "tests"  # name of folder with the tests.
TESTS_FOLDER = join(os.getcwd(), TESTS)  # path of the folder with the tests.
TESTS_OUTPUT = "output"  # name of folder with temporary output from tests.
TESTS_OUTPUT_FOLDER = join(TESTS_FOLDER, TESTS_OUTPUT)  # path of the folder with temporary output from tests.
TESTS_RESOURCES = "resources"
TESTS_RESOURCES_FOLDER = join(os.getcwd(), TESTS_RESOURCES)  # path of the folder with resources data for tests.
TESTS_LOG_NAME = "test_log.log"  # name of the log file used for tests.
