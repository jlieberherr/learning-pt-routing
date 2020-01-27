#!/usr/bin/python
# -*- coding: utf-8 -*-

from scripts.classes import Journey
from scripts.connectionscan_router import ConnectionScanCore
from scripts.helpers.funs import hhmmss_to_sec, seconds_to_hhmmss
from tests.cb_connectionscan_core_test import (
    basel_sbb, bern, bern_bahnhof, bern_duebystrasse, chur,
    create_test_connectionscan_data, ostermundigen_bahnhof, samedan,
    samedan_bahnhof, samedan_spital, st_gallen, zuerich_hb)


def a_test_unoptimized_earliest_arrival_with_reconstruction_bern_zuerich_hb():
    cs_data = create_test_connectionscan_data()
    cs_core = ConnectionScanCore(cs_data)
    journey = cs_core.route_earliest_arrival_with_reconstruction(bern.id, zuerich_hb.id, hhmmss_to_sec("08:02:00"))
    assert 1 == journey.get_nb_journey_legs()
    assert 1 == journey.get_nb_pt_journey_legs()
    assert bern.id == journey.get_first_stop_id()
    assert zuerich_hb.id == journey.get_last_stop_id()
    assert "08:02:00" == seconds_to_hhmmss(journey.get_dep_time())
    assert "08:58:00" == seconds_to_hhmmss(journey.get_arr_time())
    assert [bern.id] == journey.get_pt_in_stop_ids()
    assert [zuerich_hb.id] == journey.get_pt_out_stop_ids()

def test_unoptimized_earliest_arrival_with_reconstruction_bern_samedan():
    cs_data = create_test_connectionscan_data()
    cs_core = ConnectionScanCore(cs_data)
    journey = cs_core.route_earliest_arrival_with_reconstruction(bern.id, samedan.id, hhmmss_to_sec("08:30:00"))
    assert 3 == journey.get_nb_journey_legs()
    assert 3 == journey.get_nb_pt_journey_legs()
    assert bern.id == journey.get_first_stop_id()
    assert samedan.id == journey.get_last_stop_id()
    assert "08:32:00" == seconds_to_hhmmss(journey.get_dep_time())
    assert "12:45:00" == seconds_to_hhmmss(journey.get_arr_time())
    assert [bern.id, zuerich_hb.id, chur.id] == journey.get_pt_in_stop_ids()
    assert [zuerich_hb.id, chur.id, samedan.id] == journey.get_pt_out_stop_ids()

def test_unoptimized_earliest_arrival_with_reconstruction_bern_samedan_spital():
    cs_data = create_test_connectionscan_data()
    cs_core = ConnectionScanCore(cs_data)
    journey = cs_core.route_earliest_arrival_with_reconstruction(bern.id, samedan_spital.id, hhmmss_to_sec("07:30:00"))
    assert 4 == journey.get_nb_journey_legs()
    assert 4 == journey.get_nb_pt_journey_legs()
    assert bern.id == journey.get_first_stop_id()
    assert samedan_spital.id == journey.get_last_stop_id()
    assert "07:32:00" == seconds_to_hhmmss(journey.get_dep_time())
    assert "15:07:00" == seconds_to_hhmmss(journey.get_arr_time())
    assert [bern.id, zuerich_hb.id, chur.id, samedan_bahnhof.id] == journey.get_pt_in_stop_ids()
    assert [zuerich_hb.id, chur.id, samedan.id, samedan_spital.id] == journey.get_pt_out_stop_ids()

def test_unoptimized_earliest_arrival_with_reconstruction_bern_duebystrasse_samedan():
    cs_data = create_test_connectionscan_data()
    cs_core = ConnectionScanCore(cs_data)
    journey = cs_core.route_earliest_arrival_with_reconstruction(bern_duebystrasse.id, samedan.id, hhmmss_to_sec("07:30:00"))
    assert 4 == journey.get_nb_journey_legs()
    assert 4 == journey.get_nb_pt_journey_legs()
    assert bern_duebystrasse.id == journey.get_first_stop_id()
    assert samedan.id == journey.get_last_stop_id()
    assert "07:30:00" == seconds_to_hhmmss(journey.get_dep_time())
    assert "12:45:00" == seconds_to_hhmmss(journey.get_arr_time())
    assert [bern_duebystrasse.id, bern.id, zuerich_hb.id, chur.id] == journey.get_pt_in_stop_ids()
    assert [bern_bahnhof.id, zuerich_hb.id, chur.id, samedan.id] == journey.get_pt_out_stop_ids()

def test_unoptimized_earliest_arrival_with_reconstruction_basel_st_gallen():
    cs_data = create_test_connectionscan_data()
    cs_core = ConnectionScanCore(cs_data)
    journey = cs_core.route_earliest_arrival_with_reconstruction(basel_sbb.id, st_gallen.id, hhmmss_to_sec("07:30:00"))
    assert 2 == journey.get_nb_journey_legs()
    assert 2 == journey.get_nb_pt_journey_legs()
    assert basel_sbb.id == journey.get_first_stop_id()
    assert st_gallen.id == journey.get_last_stop_id()
    assert "07:33:00" == seconds_to_hhmmss(journey.get_dep_time())
    assert "09:41:00" == seconds_to_hhmmss(journey.get_arr_time())
    assert [basel_sbb.id, zuerich_hb.id] == journey.get_pt_in_stop_ids()
    assert [zuerich_hb.id, st_gallen.id] == journey.get_pt_out_stop_ids()

def test_unoptimized_earliest_arrival_with_reconstruction_bern_duebystrasse_ostermundigen():
    cs_data = create_test_connectionscan_data()
    cs_core = ConnectionScanCore(cs_data)
    journey = cs_core.route_earliest_arrival_with_reconstruction(bern_duebystrasse.id, ostermundigen_bahnhof.id, hhmmss_to_sec("12:09:46"))
    assert 1 == journey.get_nb_journey_legs()
    assert 1 == journey.get_nb_pt_journey_legs()
    assert bern_duebystrasse.id == journey.get_first_stop_id()
    assert ostermundigen_bahnhof.id == journey.get_last_stop_id()
    assert "12:12:00" == seconds_to_hhmmss(journey.get_dep_time())
    assert "12:34:00" == seconds_to_hhmmss(journey.get_arr_time())
    assert [bern_duebystrasse.id] == journey.get_pt_in_stop_ids()
    assert [ostermundigen_bahnhof.id] == journey.get_pt_out_stop_ids()

def test_unoptimized_earliest_arrival_with_reconstruction_bern_bern():
    cs_data = create_test_connectionscan_data()
    cs_core = ConnectionScanCore(cs_data)
    journey = cs_core.route_earliest_arrival_with_reconstruction(bern.id, bern.id, hhmmss_to_sec("12:09:46"))
    assert 0 == journey.get_nb_journey_legs()
    assert 0 == journey.get_nb_pt_journey_legs()
    assert None == journey.get_first_stop_id()
    assert None == journey.get_last_stop_id()
    assert None == seconds_to_hhmmss(journey.get_dep_time())
    assert None == seconds_to_hhmmss(journey.get_arr_time())
    assert [] == journey.get_pt_in_stop_ids()
    assert [] == journey.get_pt_out_stop_ids()

def test_unoptimized_earliest_arrival_with_reconstruction_bern_bern_bahnhof():
    cs_data = create_test_connectionscan_data()
    cs_core = ConnectionScanCore(cs_data)
    journey = cs_core.route_earliest_arrival_with_reconstruction(bern.id, bern_bahnhof.id, hhmmss_to_sec("12:09:46"))
    assert 1 == journey.get_nb_journey_legs()
    assert 0 == journey.get_nb_pt_journey_legs()
    assert bern.id == journey.get_first_stop_id()
    assert bern_bahnhof.id == journey.get_last_stop_id()
    assert None == seconds_to_hhmmss(journey.get_dep_time())
    assert None == seconds_to_hhmmss(journey.get_arr_time())
    assert [] == journey.get_pt_in_stop_ids()
    assert [] == journey.get_pt_out_stop_ids()

def test_unoptimized_earliest_arrival_with_reconstruction_bern_bahnhof_samedan():
    cs_data = create_test_connectionscan_data()
    cs_core = ConnectionScanCore(cs_data)
    journey = cs_core.route_earliest_arrival_with_reconstruction(bern_bahnhof.id, samedan.id, hhmmss_to_sec("08:26:00"))
    assert 4 == journey.get_nb_journey_legs()
    assert 3 == journey.get_nb_pt_journey_legs()
    assert bern_bahnhof.id == journey.get_first_stop_id()
    assert samedan.id == journey.get_last_stop_id()
    assert "08:27:00" == seconds_to_hhmmss(journey.get_dep_time())
    assert "12:45:00" == seconds_to_hhmmss(journey.get_arr_time())
    assert [bern.id, zuerich_hb.id, chur.id] == journey.get_pt_in_stop_ids()
    assert [zuerich_hb.id, chur.id, samedan.id] == journey.get_pt_out_stop_ids()

def test_unoptimized_earliest_arrival_with_reconstruction_bern_samedan_bahnhof():
    cs_data = create_test_connectionscan_data()
    cs_core = ConnectionScanCore(cs_data)
    journey = cs_core.route_earliest_arrival_with_reconstruction(bern.id, samedan_bahnhof.id, hhmmss_to_sec("08:30:00"))
    assert 3 == journey.get_nb_journey_legs()
    assert 3 == journey.get_nb_pt_journey_legs()
    assert bern.id == journey.get_first_stop_id()
    assert samedan_bahnhof.id == journey.get_last_stop_id()
    assert "08:32:00" == seconds_to_hhmmss(journey.get_dep_time())
    assert "12:48:00" == seconds_to_hhmmss(journey.get_arr_time())
    assert [bern.id, zuerich_hb.id, chur.id] == journey.get_pt_in_stop_ids()
    assert [zuerich_hb.id, chur.id, samedan.id] == journey.get_pt_out_stop_ids()

def test_unoptimized_earliest_arrival_with_reconstruction_bern_bahnhof_samedan_bahnhof():
    cs_data = create_test_connectionscan_data()
    cs_core = ConnectionScanCore(cs_data)
    journey = cs_core.route_earliest_arrival_with_reconstruction(bern_bahnhof.id, samedan_bahnhof.id, hhmmss_to_sec("08:26:00"))
    assert 4 == journey.get_nb_journey_legs()
    assert 3 == journey.get_nb_pt_journey_legs()
    assert bern_bahnhof.id == journey.get_first_stop_id()
    assert samedan_bahnhof.id == journey.get_last_stop_id()
    assert "08:27:00" == seconds_to_hhmmss(journey.get_dep_time())
    assert "12:48:00" == seconds_to_hhmmss(journey.get_arr_time())
    assert [bern.id, zuerich_hb.id, chur.id] == journey.get_pt_in_stop_ids()
    assert [zuerich_hb.id, chur.id, samedan.id] == journey.get_pt_out_stop_ids()

def test_unoptimized_earliest_arrival_with_reconstruction_by_name_bern_bahnhof_samedan_bahnhof():
    cs_data = create_test_connectionscan_data()
    cs_core = ConnectionScanCore(cs_data)
    journey = cs_core.route_earliest_arrival_with_reconstruction_by_name(bern_bahnhof.name, samedan_bahnhof.name, "08:26:00")
    assert 4 == journey.get_nb_journey_legs()
    assert 3 == journey.get_nb_pt_journey_legs()
    assert bern_bahnhof.id == journey.get_first_stop_id()
    assert samedan_bahnhof.id == journey.get_last_stop_id()
    assert "08:27:00" == seconds_to_hhmmss(journey.get_dep_time())
    assert "12:48:00" == seconds_to_hhmmss(journey.get_arr_time())
    assert [bern.id, zuerich_hb.id, chur.id] == journey.get_pt_in_stop_ids()
    assert [zuerich_hb.id, chur.id, samedan.id] == journey.get_pt_out_stop_ids()
