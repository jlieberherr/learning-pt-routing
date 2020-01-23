#!/usr/bin/python
# -*- coding: utf-8 -*-

from scripts.connectionscan_router import ConnectionScanCore
from scripts.helpers.funs import seconds_to_hhmmss, hhmmss_to_sec
from tests.cb_connectionscan_core_test import create_test_connectionscan_data
from tests.cb_connectionscan_core_test import bern, samedan

# TODO more tests (same as in unoptimized earliest arrival)

def test_unoptimized_earliest_arrival_with_reconstruction_bern_samedan():
    cs_data = create_test_connectionscan_data()
    cs_core = ConnectionScanCore(cs_data)
    journey = cs_core.route_earliest_arrival_with_reconstruction(bern.id, samedan.id, hhmmss_to_sec("08:30:00"))
    assert 3 == journey.get_nb_journey_legs()
    assert 3 == journey.get_nb_pt_journey_legs()
    assert bern.id == journey.get_first_stop_id()
    assert samedan.id == journey.get_last_stop_id()
    