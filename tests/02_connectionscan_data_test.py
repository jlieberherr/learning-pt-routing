#!/usr/bin/python
# -*- coding: utf-8 -*-

import pytest

from scripts.classes import Connection, Footpath, Stop, Trip
from scripts.connectionscan_router import ConnectionScanData


def test_connectionscan_data_constructor_basic():
    stops_per_id = {
        "1": Stop("1", "c1", "n1", 0.0, 0.0),
        "2": Stop("2", "c2", "n2", 1.0, 1.0),
        "2a": Stop("2a", "c2a", "n2a", 1.1, 1.1),
        "3": Stop("3", "c3", "n3", 3.0, 3.0),
    }

    footpaths_per_from_to_stop_id = {
        ("1", "1"): Footpath("1", "1", 60),
        ("2", "2"): Footpath("2", "2", 70),
        ("2a", "2a"): Footpath("2a", "2a", 71),
        ("3", "3"): Footpath("3", "3", 80),
        ("2", "2a"): Footpath("2", "2a", 75),
        ("2a", "2"): Footpath("2a", "2", 75),
    }

    con_1_1 = Connection("t1", "1", "2", 60, 70)
    con_1_2 = Connection("t1", "2", "3", 72, 80)

    con_2_1 = Connection("t2", "2", "3", 50, 59)
    con_2_2 = Connection("t2", "3", "1", 60, 72)

    trips_per_id = {
        "t1": Trip("t1", [con_1_1, con_1_2]),
        "t2": Trip("t2", [con_2_1, con_2_2])
    }
    cs_data = ConnectionScanData(stops_per_id, footpaths_per_from_to_stop_id, trips_per_id)
    assert 4 == len(cs_data.stops_per_id)
    assert 4 == len(cs_data.stops_per_id)
    assert 2 == len(cs_data.trips_per_id)
    assert [con_2_1, con_1_1, con_2_2, con_1_2] == cs_data.sorted_connections

def test_connectionscan_data_constructor_stop_id_not_consistent():
    with pytest.raises(ValueError):
        ConnectionScanData({"s1": Stop("s2", "", "", 0.0, 0.0)}, {}, {})

def test_connectionscan_data_constructor_from_stop_id_in_footpath_not_consistent():
    with pytest.raises(ValueError):
        ConnectionScanData({"s1": Stop("s1", "", "", 0.0, 0.0), "s2": Stop("s2", "", "", 0.0, 0.0)}, {("s2", "s2"): Footpath("s1", "s1", 60)}, {})

def test_connectionscan_data_constructor_to_stop_id_in_footpath_not_consistent():
    with pytest.raises(ValueError):
        ConnectionScanData({"s1": Stop("s1", "", "", 0.0, 0.0), "s2": Stop("s2", "", "", 0.0, 0.0)}, {("s2", "s1"): Footpath("s2", "s2", 60)}, {})

def test_connectionscan_data_constructor_stops_in_footpath_and_stops_not_consistent():
    with pytest.raises(ValueError):
        ConnectionScanData({"s1": Stop("s1", "", "", 0.0, 0.0)}, {("s1", "s2"): Footpath("s1", "s2", 60)}, {})

def test_connectionscan_data_constructor_trip_id_not_consistent():
    with pytest.raises(ValueError):
        ConnectionScanData({}, {}, {"t1": Trip("t", [])})

def test_connectionscan_data_constructor_stop_ids_in_trips_not_consistent_with_stops():
    with pytest.raises(ValueError):
        ConnectionScanData({"s1": Stop("s1", "", "", 0.0, 0.0)}, {}, {"t": Trip("t", [Connection("t", "s1", "s2", 30, 40)])})
