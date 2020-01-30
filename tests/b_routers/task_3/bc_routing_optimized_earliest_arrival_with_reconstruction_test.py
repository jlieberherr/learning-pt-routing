#!/usr/bin/python
# -*- coding: utf-8 -*-
from tests.b_routers.template_routing_earliest_arrival_with_reconstruction_test import RouterWithReconstructionType, \
    run_tests


def test_unoptimized_earliest_arrival_with_reconstruction():
    run_tests(RouterWithReconstructionType.OPTIMIZED_EARLIEST_ARRIVAL_WITH_RECONSTRUCTION)
