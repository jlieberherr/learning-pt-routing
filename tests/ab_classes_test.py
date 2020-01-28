#!/usr/bin/python
# -*- coding: utf-8 -*-

import pytest

from scripts.classes import Connection, Footpath, Stop, Trip, JourneyLeg, Journey


def test_stop_constructor():
    a_stop = Stop("1", "c1", "n1", 23.4, 56.6)
    assert "1" == a_stop.id
    assert "c1" == a_stop.code
    assert "n1" == a_stop.name
    assert 23.4 == a_stop.easting
    assert 56.6 == a_stop.northing


def test_footpath_constructor():
    a_footpath = Footpath("1", "2", 60)
    assert "1" == a_footpath.from_stop_id
    assert "2" == a_footpath.to_stop_id
    assert 60 == a_footpath.walking_time


def test_connection_constructor_basic():
    a_connection = Connection("t1", "1", "2", 60, 120)
    assert "t1" == a_connection.trip_id
    assert "1" == a_connection.from_stop_id
    assert "2" == a_connection.to_stop_id
    assert 60 == a_connection.dep_time
    assert 120 == a_connection.arr_time


def test_connection_constructor_not_time_consistent():
    with pytest.raises(ValueError):
        Connection("t1", "1", "2", 60, 50)


def test_trip_constructor_basic():
    trip_id = "t1"
    connections = [
        Connection(trip_id, "s1", "s2", 60, 70),
        Connection(trip_id, "s2", "s3", 72, 80),
        Connection(trip_id, "s3", "s4", 82, 90),
    ]
    a_trip = Trip(trip_id, connections)
    assert trip_id == a_trip.id
    assert 3 == len(a_trip.connections)
    assert "s2" == a_trip.connections[1].from_stop_id
    assert 90 == a_trip.connections[2].arr_time


def test_trip_constructor_not_time_consistent():
    trip_id = "t1"
    connections = [
        Connection(trip_id, "s1", "s2", 60, 70),
        Connection(trip_id, "s2", "s3", 68, 80),
    ]
    with pytest.raises(ValueError):
        Trip(trip_id, connections)


def test_trip_constructor_not_stop_consistent():
    trip_id = "t1"
    connections = [
        Connection(trip_id, "s1", "s2", 60, 70),
        Connection(trip_id, "s3", "s4", 70, 80),
    ]
    with pytest.raises(ValueError):
        Trip(trip_id, connections)


def test_trip_get_all_from_stop_ids():
    trip_id = "t1"
    connections = [
        Connection(trip_id, "s1", "s2", 60, 70),
        Connection(trip_id, "s2", "s3", 70, 80),
    ]
    a_trip = Trip(trip_id, connections)
    assert ["s1", "s2"] == a_trip.get_all_from_stop_ids()


def test_trip_get_all_to_stop_ids():
    trip_id = "t1"
    connections = [
        Connection(trip_id, "s1", "s2", 60, 70),
        Connection(trip_id, "s2", "s3", 70, 80),
    ]
    a_trip = Trip(trip_id, connections)
    assert ["s2", "s3"] == a_trip.get_all_to_stop_ids()


def test_trip_get_set_of_all_stop_ids():
    trip_id = "t1"
    connections = [
        Connection(trip_id, "s1", "s2", 60, 70),
        Connection(trip_id, "s2", "s3", 70, 80),
    ]
    a_trip = Trip(trip_id, connections)
    assert {"s1", "s2", "s3"} == a_trip.get_set_of_all_stop_ids()


def test_journey_leg():
    in_connection = Connection("t1", "s1", "s2", 10, 20)
    out_connection = Connection("t1", "s5", "s6", 30, 40)
    footpath = Footpath("s6", "s7", 1)
    journey_leg = JourneyLeg(in_connection, out_connection, footpath)
    assert in_connection == journey_leg.in_connection
    assert out_connection == journey_leg.out_connection
    assert footpath == journey_leg.footpath
    assert "t1" == journey_leg.get_trip_id()
    assert "s1" == journey_leg.get_in_stop_id()
    assert "s6" == journey_leg.get_out_stop_id()
    assert "s1" == journey_leg.get_first_stop_id()
    assert "s7" == journey_leg.get_last_stop_id()
    assert 10 == journey_leg.get_dep_time_in_stop_id()
    assert 40 == journey_leg.get_arr_time_out_stop_id()


def test_journey_leg_without_footpath():
    in_connection = Connection("t1", "s1", "s2", 10, 20)
    out_connection = Connection("t1", "s5", "s6", 30, 40)
    journey_leg = JourneyLeg(in_connection, out_connection, None)
    assert in_connection == journey_leg.in_connection
    assert out_connection == journey_leg.out_connection
    assert journey_leg.footpath is None
    assert "t1" == journey_leg.get_trip_id()
    assert "s1" == journey_leg.get_in_stop_id()
    assert "s6" == journey_leg.get_out_stop_id()
    assert 10 == journey_leg.get_dep_time_in_stop_id()
    assert 40 == journey_leg.get_arr_time_out_stop_id()


def test_journey_leg_without_in_out_connection():
    footpath = Footpath("s6", "s7", 1)
    journey_leg = JourneyLeg(None, None, footpath)
    assert journey_leg.in_connection is None
    assert journey_leg.out_connection is None
    assert footpath == journey_leg.footpath
    assert journey_leg.get_in_stop_id() is None
    assert journey_leg.get_out_stop_id() is None
    assert journey_leg.get_dep_time_in_stop_id() is None
    assert journey_leg.get_arr_time_out_stop_id() is None


def test_journey_leg_constructor_not_trip_consistent():
    in_connection = Connection("t1", "s1", "s2", 10, 20)
    out_connection = Connection("t2", "s5", "s6", 30, 40)
    footpath = Footpath("s6", "s7", 1)
    with pytest.raises(ValueError):
        JourneyLeg(in_connection, out_connection, footpath)


def test_journey_leg_constructor_not_time_consistent():
    in_connection = Connection("t1", "s1", "s2", 10, 20)
    out_connection = Connection("t1", "s5", "s6", 5, 9)
    footpath = Footpath("s6", "s7", 1)
    with pytest.raises(ValueError):
        JourneyLeg(in_connection, out_connection, footpath)


def test_journey_leg_constructor_not_stop_consistent():
    in_connection = Connection("t1", "s1", "s2", 10, 20)
    out_connection = Connection("t1", "s5", "s6", 30, 40)
    footpath = Footpath("s10", "s7", 1)
    with pytest.raises(ValueError):
        JourneyLeg(in_connection, out_connection, footpath)


def test_journey_leg_constructor_not_in_out_connection_consistent_1():
    in_connection = Connection("t1", "s1", "s2", 10, 20)
    out_connection = None
    footpath = Footpath("s10", "s7", 1)
    with pytest.raises(ValueError):
        JourneyLeg(in_connection, out_connection, footpath)


def test_journey_leg_constructor_not_in_out_connection_consistent_2():
    in_connection = None
    out_connection = Connection("t1", "s5", "s6", 30, 40)
    footpath = Footpath("s10", "s7", 1)
    with pytest.raises(ValueError):
        JourneyLeg(in_connection, out_connection, footpath)


def test_journey_leg_1():
    journey = Journey()
    journey.prepend_journey_leg(
        JourneyLeg(Connection("t2", "s7", "s8", 50, 60), Connection("t2", "s12", "s13", 80, 90), None))
    journey.prepend_journey_leg(
        JourneyLeg(Connection("t1", "s1", "s2", 10, 20), Connection("t1", "s5", "s6", 30, 40), Footpath("s6", "s7", 1)))
    journey.prepend_journey_leg(JourneyLeg(None, None, Footpath("s0", "s1", 2)))
    assert journey.has_legs()
    assert journey.is_first_leg_footpath()
    assert not journey.is_last_leg_footpath()
    assert "s0" == journey.get_first_stop_id()
    assert "s13" == journey.get_last_stop_id()
    assert 3 == journey.get_nb_journey_legs()
    assert 2 == journey.get_nb_pt_journey_legs()


def test_journey_leg_2():
    journey = Journey()
    journey.prepend_journey_leg(JourneyLeg(Connection("t2", "s6", "s8", 50, 60), Connection("t2", "s12", "s13", 80, 90),
                                           Footpath("s13", "s14", 1)))
    journey.prepend_journey_leg(
        JourneyLeg(Connection("t1", "s1", "s2", 10, 20), Connection("t1", "s5", "s6", 30, 40), None))
    assert journey.has_legs()
    assert not journey.is_first_leg_footpath()
    assert journey.is_last_leg_footpath()
    assert "s1" == journey.get_first_stop_id()
    assert "s14" == journey.get_last_stop_id()
    assert 2 == journey.get_nb_journey_legs()
    assert 2 == journey.get_nb_pt_journey_legs()


def test_journey_prepend_journey_leg_not_stop_consistent_1():
    journey = Journey()
    journey.prepend_journey_leg(
        JourneyLeg(Connection("t2", "s6", "s8", 50, 60), Connection("t2", "s12", "s13", 80, 90), None))
    with pytest.raises(ValueError):
        journey.prepend_journey_leg(
            JourneyLeg(Connection("t1", "s1", "s2", 10, 20), Connection("t1", "s5", "s6", 30, 40),
                       Footpath("s6", "s7", 1)))


def test_journey_prepend_journey_leg_not_stop_consistent_2():
    journey = Journey()
    journey.prepend_journey_leg(
        JourneyLeg(Connection("t2", "s6", "s8", 50, 60), Connection("t2", "s12", "s13", 80, 90), None))
    with pytest.raises(ValueError):
        journey.prepend_journey_leg(
            JourneyLeg(Connection("t1", "s1", "s2", 10, 20), Connection("t1", "s5", "s7", 30, 40), None))
