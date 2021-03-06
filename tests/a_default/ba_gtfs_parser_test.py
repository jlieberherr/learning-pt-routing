#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import date
from zipfile import ZipFile

import pytest

from scripts.classes import Stop, Footpath, TripType
from scripts.gtfs_parser import (get_service_available_at_date_per_service_id,
                                 get_trip_available_at_date_per_trip_id,
                                 parse_gtfs,
                                 create_beeline_footpaths)
from scripts.connectionscan_router import make_transitive
from scripts.helpers.funs import hhmmss_to_sec

PATH_GTFS_TEST_SAMPLE = "tests/resources/gtfsfp20192018-12-05_small.zip"


def test_gtfs_parser():
    cs_data = parse_gtfs(PATH_GTFS_TEST_SAMPLE, date(2019, 1, 18), beeline_distance=200)

    # stops
    assert 89 + 11 == len(cs_data.stops_per_id)

    def check_stop(stop_id, exp_code, exp_name, exp_easting, exp_northing, exp_is_station, exp_parent_station_id):
        a_stop = cs_data.stops_per_id[stop_id]
        assert stop_id == a_stop.id
        assert exp_code == a_stop.code
        assert exp_name == a_stop.name
        assert exp_easting == a_stop.easting
        assert exp_northing == a_stop.northing
        assert exp_is_station == a_stop.is_station
        assert (exp_parent_station_id if exp_parent_station_id else None) == a_stop.parent_station_id

    check_stop("8500218:0:7", "", "Olten", 7.90768978414808, 47.3522319182299, False, "8500218P")
    check_stop("8587654", "", "Glattbrugg, Glatthof", 8.56762812456551, 47.434511142518, False, None)
    check_stop("8594553", "", "Opfikon, Schwimmbad", 8.57155376235766, 47.4326456250948, False, None)
    check_stop("8501008P", "", "Genève", 6.14245533484329, 46.2102053471586, True, None)

    # footpaths
    assert (168 + (2 * 35) + (89 + 11) + 10) == len(cs_data.footpaths_per_from_to_stop_id)

    def check_footpath(from_stop_id, to_stop_id, exp_walking_time):
        a_footpath = cs_data.footpaths_per_from_to_stop_id[(from_stop_id, to_stop_id)]
        assert from_stop_id == a_footpath.from_stop_id
        assert to_stop_id == a_footpath.to_stop_id
        assert exp_walking_time == a_footpath.walking_time

    check_footpath("8500218:0:8", "8500218:0:7", 300)
    check_footpath("8503000:0:34", "8503000:0:14", 420)
    check_footpath("8501026:0:3", "8501026:0:1", 120)
    check_footpath("8500218:0:7", "8500218P", 0)
    check_footpath("8500218P", "8500218:0:7", 0)
    check_footpath("8500218P", "8500218P", 0)
    check_footpath("8503000:0:34", "8503000:0:34", 0)

    # trips
    def check_trip(trip_id, exp_nb_connections, exp_first_stop_id, exp_last_stop_id, exp_dep_first_stop,
                   exp_arr_last_stop, exp_trip_type=None):
        trip = cs_data.trips_per_id[trip_id]
        assert exp_nb_connections == len(trip.connections)
        first_con = trip.connections[0]
        last_con = trip.connections[-1]
        assert exp_first_stop_id == first_con.from_stop_id
        assert exp_last_stop_id == last_con.to_stop_id
        assert hhmmss_to_sec(exp_dep_first_stop) == first_con.dep_time
        assert hhmmss_to_sec(exp_arr_last_stop) == last_con.arr_time
        if exp_trip_type is not None:
            assert exp_trip_type == trip.trip_type

    check_trip("2.TA.1-85-j19-1.1.H", 16, "8572668", "8572648", "06:01:00", "06:23:00")
    check_trip("1.TA.1-85-j19-1.1.H", 16, "8572668", "8572648", "05:31:00", "05:53:00", exp_trip_type=TripType.UNKNOWN)

    def check_connection_on_trip(trip_id, connection_index, exp_from_stop_id, exp_to_stop_id, exp_dep_time_hhmmss,
                                 exp_arr_time_hhmmss):
        trip = cs_data.trips_per_id[trip_id]
        con = trip.connections[connection_index]
        assert exp_from_stop_id == con.from_stop_id
        assert exp_to_stop_id == con.to_stop_id
        assert hhmmss_to_sec(exp_dep_time_hhmmss) == con.dep_time
        assert hhmmss_to_sec(exp_arr_time_hhmmss) == con.arr_time

    check_connection_on_trip("2.TA.1-85-j19-1.1.H", 0, "8572668", "8502095", "06:01:00", "06:04:00")
    check_connection_on_trip("2.TA.1-85-j19-1.1.H", 1, "8502095", "8572666", "06:04:00", "06:05:00")
    check_connection_on_trip("2.TA.1-85-j19-1.1.H", 1, "8502095", "8572666", "06:04:00", "06:05:00")
    check_connection_on_trip("2.TA.1-85-j19-1.1.H", 15, "8572656", "8572648", "06:18:00", "06:23:00")

    with pytest.raises(KeyError):
        # noinspection PyStatementEffect
        cs_data.trips_per_id["3.TA.90-73-Y-j19-1.2.H"]

    with pytest.raises(KeyError):
        # noinspection PyStatementEffect
        cs_data.trips_per_id["471.TA.26-759-j19-1.5.R"]


def test_get_service_available_at_date_per_service_id_get_trip_available_at_date_per_trip_id():
    with ZipFile(PATH_GTFS_TEST_SAMPLE, "r") as zip_file:
        # calendar.txt and # calendar_dates.txt
        service_available_at_date_per_service_id = \
            get_service_available_at_date_per_service_id(zip_file, date(2019, 1, 18))
        # 2019-01-18 was a friday
        assert 46 == len(service_available_at_date_per_service_id)
        assert service_available_at_date_per_service_id["TA+b0001"]
        assert not service_available_at_date_per_service_id["TA+b02i1"]
        assert not service_available_at_date_per_service_id["TA+b00va"]  # removed by calendar_dates.txt
        assert service_available_at_date_per_service_id["TA+b02ro"]
        assert not service_available_at_date_per_service_id["TA+b03ur"]  # removed by calendar_dates.txt

        # trips.txt
        trip_available_at_date_per_trip_id, route_id_per_trip_id = \
            get_trip_available_at_date_per_trip_id(zip_file, service_available_at_date_per_service_id)
        assert 2272 == len(trip_available_at_date_per_trip_id)
        assert trip_available_at_date_per_trip_id["1.TA.1-85-j19-1.1.H"]
        assert trip_available_at_date_per_trip_id["2.TA.1-85-j19-1.1.H"]
        assert not trip_available_at_date_per_trip_id["471.TA.26-759-j19-1.5.R"]
        assert not trip_available_at_date_per_trip_id["6.TA.6-1-j19-1.6.R"]
        assert trip_available_at_date_per_trip_id["18.TA.6-1-j19-1.17.H"]
        assert not trip_available_at_date_per_trip_id["41.TA.6-1-j19-1.37.R"]
        assert not trip_available_at_date_per_trip_id["3.TA.90-73-Y-j19-1.2.H"]

        assert 2272 == len(route_id_per_trip_id)
        assert "1-85-j19-1" == route_id_per_trip_id["2.TA.1-85-j19-1.1.H"]
        assert "26-759-j19-1" == route_id_per_trip_id["6.TA.26-759-j19-1.1.R"]
        assert "6-1-j19-1" == route_id_per_trip_id["41.TA.6-1-j19-1.37.R"]


def test_create_beeline_footpaths():
    wattwil = Stop("Wattwil", "", "", 9.0864591001338, 47.2994765484827)
    wattwil_bahnhof = Stop("Wattwil, Bahnhof", "", "", 9.08679147678897, 47.2994582722627)
    pontresina = Stop("Pontresina", "", "", 9.89607473321206, 46.4906506582138)
    pontresina_bahnhof = Stop("Pontresina, Bahnhof", "", "", 9.89608371636491, 46.4910341056312)
    pontresina_post = Stop("Pontresina, Post", "", "", 9.90654010627351, 46.4880901497136)
    bern = Stop("Bern", "", "", 7.43911954873327, 46.9488249647708)
    bern_bahnhof = Stop("Bern, Bahnhof", "", "", 7.44020651022721, 46.948107473715)
    stops = [
        wattwil,
        wattwil_bahnhof,
        pontresina,
        pontresina_bahnhof,
        pontresina_post,
        bern,
        bern_bahnhof
    ]
    stops_per_id = {s.id: s for s in stops}
    footpaths = {
        Footpath(wattwil.id, wattwil_bahnhof.id, 120),
        Footpath(wattwil_bahnhof.id, wattwil.id, 120),
    }
    footpaths_per_from_to_stop_id = {(f.from_stop_id, f.to_stop_id): f for f in footpaths}
    create_beeline_footpaths(stops_per_id, footpaths_per_from_to_stop_id, beeline_distance=100, walking_speed=2 / 3.6)
    assert 120 == footpaths_per_from_to_stop_id[wattwil.id, wattwil_bahnhof.id].walking_time
    assert 120 == footpaths_per_from_to_stop_id[wattwil_bahnhof.id, wattwil.id].walking_time
    assert (pontresina.id, pontresina_bahnhof.id) in footpaths_per_from_to_stop_id
    assert (pontresina_bahnhof.id, pontresina.id) in footpaths_per_from_to_stop_id
    assert (pontresina.id, pontresina_post.id) not in footpaths_per_from_to_stop_id
    assert (pontresina_post.id, pontresina.id) not in footpaths_per_from_to_stop_id
    assert (bern.id, bern_bahnhof.id) not in footpaths_per_from_to_stop_id
    assert (bern_bahnhof.id, bern.id) not in footpaths_per_from_to_stop_id


def test_make_transitive_simple():
    footpaths = [
        Footpath("s1", "s2", 60),
        Footpath("s2", "s3", 70),
    ]

    footpaths_per_from_to_stop_id = {(f.from_stop_id, f.to_stop_id): f for f in footpaths}

    make_transitive(footpaths_per_from_to_stop_id)

    assert 3 == len(footpaths_per_from_to_stop_id)

    footpath_s1_s3 = footpaths_per_from_to_stop_id[("s1", "s3")]
    assert "s1" == footpath_s1_s3.from_stop_id
    assert "s3" == footpath_s1_s3.to_stop_id
    assert 130 == footpath_s1_s3.walking_time


def test_make_transitive_two_iterations():
    footpaths = [
        Footpath("s1", "s2", 60),
        Footpath("s2", "s3", 70),
        Footpath("s3", "s4", 70),
    ]

    footpaths_per_from_to_stop_id = {(f.from_stop_id, f.to_stop_id): f for f in footpaths}

    make_transitive(footpaths_per_from_to_stop_id)

    assert 6 == len(footpaths_per_from_to_stop_id)

    assert 130 == footpaths_per_from_to_stop_id[("s1", "s3")].walking_time
    assert 200 == footpaths_per_from_to_stop_id[("s1", "s4")].walking_time
    assert 140 == footpaths_per_from_to_stop_id[("s2", "s4")].walking_time


def test_make_tranksitive_change_time():
    footpaths = [
        Footpath("s1", "s2", 60),
        Footpath("s2", "s3", 70),
        Footpath("s1", "s3", 140),
    ]

    footpaths_per_from_to_stop_id = {(f.from_stop_id, f.to_stop_id): f for f in footpaths}

    make_transitive(footpaths_per_from_to_stop_id)

    assert 3 == len(footpaths_per_from_to_stop_id)
    assert 130 == footpaths_per_from_to_stop_id[("s1", "s3")].walking_time


def test_make_transitive_nothing_to_do():
    footpaths = [
        Footpath("s1", "s2", 60),
        Footpath("s2", "s3", 70),
        Footpath("s1", "s3", 90),
    ]

    footpaths_per_from_to_stop_id = {(f.from_stop_id, f.to_stop_id): f for f in footpaths}

    make_transitive(footpaths_per_from_to_stop_id)

    assert 3 == len(footpaths_per_from_to_stop_id)
