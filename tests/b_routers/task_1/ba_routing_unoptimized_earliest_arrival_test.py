#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for unoptimized earliest arrival routing (task 1)."""
from scripts.connectionscan_router import ConnectionScanCore
from scripts.helpers.funs import seconds_to_hhmmss, hhmmss_to_sec
from tests.a_default.cb_connectionscan_core_test import (bern, zuerich_hb, samedan, samedan_spital, bern_duebystrasse,
                                                         basel_sbb, st_gallen, ostermundigen_bahnhof, bern_bahnhof)
from tests.a_default.cb_connectionscan_core_test import create_test_connectionscan_data


def test_unoptimized_earliest_arrival_bern_zuerich_hb():
    cs_data = create_test_connectionscan_data()
    cs_core = ConnectionScanCore(cs_data)
    assert "08:58:00" == seconds_to_hhmmss(
        cs_core.route_earliest_arrival(bern.id, zuerich_hb.id, hhmmss_to_sec("07:35:00")))
    assert "08:58:00" == seconds_to_hhmmss(
        cs_core.route_earliest_arrival(bern.id, zuerich_hb.id, hhmmss_to_sec("08:02:00")))
    assert cs_core.route_earliest_arrival(bern.id, zuerich_hb.id, hhmmss_to_sec("23:33:00")) is None


def test_unoptimized_earliest_arrival_bern_samedan():
    cs_data = create_test_connectionscan_data()
    cs_core = ConnectionScanCore(cs_data)
    assert "12:45:00" == seconds_to_hhmmss(
        cs_core.route_earliest_arrival(bern.id, samedan.id, hhmmss_to_sec("08:30:00")))
    assert cs_core.route_earliest_arrival(bern.id, samedan.id, hhmmss_to_sec("21:00:00")) is None


def test_unoptimized_earliest_arrival_bern_samedan_spital():
    cs_data = create_test_connectionscan_data()
    cs_core = ConnectionScanCore(cs_data)
    assert "15:07:00" == seconds_to_hhmmss(
        cs_core.route_earliest_arrival(bern.id, samedan_spital.id, hhmmss_to_sec("07:30:00")))


def test_unoptimized_earliest_arrival_bern_duebystrasse_samedan():
    cs_data = create_test_connectionscan_data()
    cs_core = ConnectionScanCore(cs_data)
    assert "12:45:00" == seconds_to_hhmmss(
        cs_core.route_earliest_arrival(bern_duebystrasse.id, samedan.id, hhmmss_to_sec("07:30:00")))


def test_unoptimized_earliest_arrival_basel_st_gallen():
    cs_data = create_test_connectionscan_data()
    cs_core = ConnectionScanCore(cs_data)
    assert "09:41:00" == seconds_to_hhmmss(
        cs_core.route_earliest_arrival(basel_sbb.id, st_gallen.id, hhmmss_to_sec("07:30:00")))


def test_unoptimized_earliest_arrival_bern_duebystrasse_ostermundigen_bahnhof():
    cs_data = create_test_connectionscan_data()
    cs_core = ConnectionScanCore(cs_data)
    assert "12:34:00" == seconds_to_hhmmss(
        cs_core.route_earliest_arrival(bern_duebystrasse.id, ostermundigen_bahnhof.id, hhmmss_to_sec("12:09:46")))


def test_unoptimized_earliest_arrival_bern_bern():
    cs_data = create_test_connectionscan_data()
    cs_core = ConnectionScanCore(cs_data)
    assert "12:09:46" == seconds_to_hhmmss(cs_core.route_earliest_arrival(bern.id, bern.id, hhmmss_to_sec("12:09:46")))


def test_unoptimized_earliest_arrival_bern_bern_bahnhof():
    cs_data = create_test_connectionscan_data()
    cs_core = ConnectionScanCore(cs_data)
    assert "12:14:46" == seconds_to_hhmmss(
        cs_core.route_earliest_arrival(bern.id, bern_bahnhof.id, hhmmss_to_sec("12:09:46")))


def test_unoptimized_earliest_arrival_by_name_bern_bern_bahnhof():
    cs_data = create_test_connectionscan_data()
    cs_core = ConnectionScanCore(cs_data)
    assert "12:14:46" == seconds_to_hhmmss(
        cs_core.route_earliest_arrival_by_name(bern.name, bern_bahnhof.name, "12:09:46"))
