import pytest

from scripts.classes import Connection, Footpath, Stop, Trip


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

def test_trip_get_set_of_all_stop_idss():
    trip_id = "t1"
    connections = [
        Connection(trip_id, "s1", "s2", 60, 70),
        Connection(trip_id, "s2", "s3", 70, 80),
    ]
    a_trip = Trip(trip_id, connections)
    assert {"s1", "s2", "s3"} == a_trip.get_set_of_all_stop_ids()
