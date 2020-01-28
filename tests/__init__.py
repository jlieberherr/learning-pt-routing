#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

from scripts.helpers.my_logging import init_logging
from scripts.helpers.project_params import TESTS_OUTPUT_FOLDER, TESTS_LOG_NAME

init_logging(TESTS_OUTPUT_FOLDER, TESTS_LOG_NAME)
