from scripts.classes import Connection, Footpath, Stop


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

def test_connection_constructor():
    a_connection = Connection("1", "2", 60, 120)
    assert "1" == a_connection.from_stop_id
    assert "2" == a_connection.to_stop_id
    assert 60 == a_connection.dep_time
    assert 120 == a_connection.arr_time
