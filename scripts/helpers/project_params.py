#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from os.path import join

OUTPUT = "output"
OUTPUT_FOLDER = join(os.getcwd(), OUTPUT)
RESOURCES = "resources"
RESOURCES_FOLDER = join(os.getcwd(), RESOURCES)
LOG_NAME = "log.log"

# tests
TESTS = "tests"
TESTS_FOLDER = join(os.getcwd(), TESTS)
TESTS_OUTPUT = "output"
TESTS_OUTPUT_FOLDER = join(TESTS_FOLDER, TESTS_OUTPUT)
TESTS_RESOURCES = "resources"
TESTS_RESOURCES_FOLDER = join(os.getcwd(), TESTS_RESOURCES)
TESTS_LOG_NAME = "test_log.log"
