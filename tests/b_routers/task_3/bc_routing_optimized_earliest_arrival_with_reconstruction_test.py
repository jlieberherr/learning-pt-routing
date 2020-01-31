#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for optimized earliest arrival routing (task 3)."""
from tests.b_routers.template_routing_earliest_arrival_with_reconstruction_test import RouterWithReconstructionType, \
    run_tests


def test_unoptimized_earliest_arrival_with_reconstruction():
    run_tests(RouterWithReconstructionType.OPTIMIZED_EARLIEST_ARRIVAL_WITH_RECONSTRUCTION)
