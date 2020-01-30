#!/usr/bin/python
# -*- coding: utf-8 -*-
from scripts.connectionscan_router import ConnectionScanCore
from scripts.helpers.funs import seconds_to_hhmmss
from tests.a_default.cb_connectionscan_core_test import create_test_connectionscan_data, bern_bahnhof, samedan_bahnhof, \
    bern, zuerich_hb, chur, samedan
from tests.b_routers.template_routing_earliest_arrival_with_reconstruction_test import RouterWithReconstructionType, \
    run_tests


def test_unoptimized_earliest_arrival_with_reconstruction():
    run_tests(RouterWithReconstructionType.UNOPTIMIZED_EARLIEST_ARRIVAL_WITH_RECONSTRUCTION)


def test_unoptimized_earliest_arrival_with_reconstruction_by_name_bern_bahnhof_samedan_bahnhof():
    cs_data = create_test_connectionscan_data()
    cs_core = ConnectionScanCore(cs_data)
    journey = cs_core.route_earliest_arrival_with_reconstruction_by_name(bern_bahnhof.name, samedan_bahnhof.name,
                                                                         "08:26:00")
    assert 4 == journey.get_nb_journey_legs()
    assert 3 == journey.get_nb_pt_journey_legs()
    assert bern_bahnhof.id == journey.get_first_stop_id()
    assert samedan_bahnhof.id == journey.get_last_stop_id()
    assert "08:27:00" == seconds_to_hhmmss(journey.get_dep_time())
    assert "12:48:00" == seconds_to_hhmmss(journey.get_arr_time())
    assert [bern.id, zuerich_hb.id, chur.id] == journey.get_pt_in_stop_ids()
    assert [zuerich_hb.id, chur.id, samedan.id] == journey.get_pt_out_stop_ids()
