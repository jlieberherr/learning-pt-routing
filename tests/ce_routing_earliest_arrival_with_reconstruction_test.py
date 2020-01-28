#!/usr/bin/python
# -*- coding: utf-8 -*-

from scripts.connectionscan_router import ConnectionScanCore
from scripts.helpers.funs import hhmmss_to_sec, seconds_to_hhmmss
from tests.cb_connectionscan_core_test import (
    basel_sbb, bern, bern_bahnhof, bern_duebystrasse, chur,
    create_test_connectionscan_data, ostermundigen_bahnhof, samedan,
    samedan_bahnhof, samedan_spital, st_gallen, zuerich_hb)


def run_router_with_reconstruction_test(
        from_stop,
        to_stop,
        des_dep_time_hhmmss,
        exp_nb_legs,
        exp_nb_pt_legs,
        exp_first_stop,
        exp_last_stop,
        exp_dep_time_hhmmss,
        exp_arr_time_hhmmss,
        exp_pt_in_stops,
        exp_pt_out_stops):
    cs_data = create_test_connectionscan_data()
    cs_core = ConnectionScanCore(cs_data)
    for router in [cs_core.route_earliest_arrival_with_reconstruction,
                   cs_core.route_optimized_earliest_arrival_with_reconstruction]:
        journey = router(from_stop.id, to_stop.id, hhmmss_to_sec(des_dep_time_hhmmss))
        assert exp_nb_legs == journey.get_nb_journey_legs()
        assert exp_nb_pt_legs == journey.get_nb_pt_journey_legs()
        assert (exp_first_stop.id if exp_first_stop is not None else None) == journey.get_first_stop_id()
        assert (exp_last_stop.id if exp_last_stop is not None else None) == journey.get_last_stop_id()
        assert (exp_dep_time_hhmmss if exp_dep_time_hhmmss else None) == seconds_to_hhmmss(journey.get_dep_time())
        assert (exp_arr_time_hhmmss if exp_arr_time_hhmmss else None) == seconds_to_hhmmss(journey.get_arr_time())
        assert [s.id for s in exp_pt_in_stops] == journey.get_pt_in_stop_ids()
        assert [s.id for s in exp_pt_out_stops] == journey.get_pt_out_stop_ids()


def test_earliest_arrival_with_reconstruction_bern_zuerich_hb():
    run_router_with_reconstruction_test(
        bern,
        zuerich_hb,
        "08:02:00",
        1,
        1,
        bern,
        zuerich_hb,
        "08:02:00",
        "08:58:00",
        [bern],
        [zuerich_hb]
    )


def test_earliest_arrival_with_reconstruction_bern_samedan():
    run_router_with_reconstruction_test(
        bern,
        samedan,
        "08:30:00",
        3,
        3,
        bern,
        samedan,
        "08:32:00",
        "12:45:00",
        [bern, zuerich_hb, chur],
        [zuerich_hb, chur, samedan]
    )


def test_earliest_arrival_with_reconstruction_bern_samedan_spital():
    run_router_with_reconstruction_test(
        bern,
        samedan_spital,
        "07:30:00",
        4,
        4,
        bern,
        samedan_spital,
        "07:32:00",
        "15:07:00",
        [bern, zuerich_hb, chur, samedan_bahnhof],
        [zuerich_hb, chur, samedan, samedan_spital]
    )


def test_earliest_arrival_with_reconstruction_bern_duebystrasse_samedan():
    run_router_with_reconstruction_test(
        bern_duebystrasse,
        samedan,
        "07:30:00",
        4,
        4,
        bern_duebystrasse,
        samedan,
        "07:30:00",
        "12:45:00",
        [bern_duebystrasse, bern, zuerich_hb, chur],
        [bern_bahnhof, zuerich_hb, chur, samedan]
    )


def test_earliest_arrival_with_reconstruction_basel_st_gallen():
    run_router_with_reconstruction_test(
        basel_sbb,
        st_gallen,
        "07:30:00",
        2,
        2,
        basel_sbb,
        st_gallen,
        "07:33:00",
        "09:41:00",
        [basel_sbb, zuerich_hb],
        [zuerich_hb, st_gallen]
    )


def test_earliest_arrival_with_reconstruction_bern_duebystrasse_ostermundigen():
    run_router_with_reconstruction_test(
        bern_duebystrasse,
        ostermundigen_bahnhof,
        "12:09:46",
        1,
        1,
        bern_duebystrasse,
        ostermundigen_bahnhof,
        "12:12:00",
        "12:34:00",
        [bern_duebystrasse],
        [ostermundigen_bahnhof]
    )


def test_earliest_arrival_with_reconstruction_bern_bern():
    run_router_with_reconstruction_test(
        bern,
        bern,
        "12:09:46",
        0,
        0,
        None,
        None,
        None,
        None,
        [],
        []
    )


def test_earliest_arrival_with_reconstruction_bern_bern_bahnhof():
    run_router_with_reconstruction_test(
        bern,
        bern_bahnhof,
        "12:09:46",
        1,
        0,
        bern,
        bern_bahnhof,
        None,
        None,
        [],
        []
    )


def test_earliest_arrival_with_reconstruction_bern_bahnhof_samedan():
    run_router_with_reconstruction_test(
        bern_bahnhof,
        samedan,
        "08:26:00",
        4,
        3,
        bern_bahnhof,
        samedan,
        "08:27:00",
        "12:45:00",
        [bern, zuerich_hb, chur],
        [zuerich_hb, chur, samedan]
    )


def test_earliest_arrival_with_reconstruction_bern_samedan_bahnhof():
    run_router_with_reconstruction_test(
        bern,
        samedan_bahnhof,
        "08:30:00",
        3,
        3,
        bern,
        samedan_bahnhof,
        "08:32:00",
        "12:48:00",
        [bern, zuerich_hb, chur],
        [zuerich_hb, chur, samedan]
    )


def test_earliest_arrival_with_reconstruction_bern_bahnhof_samedan_bahnhof():
    run_router_with_reconstruction_test(
        bern_bahnhof,
        samedan_bahnhof,
        "08:26:00",
        4,
        3,
        bern_bahnhof,
        samedan_bahnhof,
        "08:27:00",
        "12:48:00",
        [bern, zuerich_hb, chur],
        [zuerich_hb, chur, samedan]
    )


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
