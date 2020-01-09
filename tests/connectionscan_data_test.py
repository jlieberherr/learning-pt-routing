from scripts.classes import Stop, Footpath, Connection
from scripts.connectionscan_router import ConnectionScanData


def test_connectionscan_data_constructor():
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

    trips_per_id = [] # TODO
    cs_data = ConnectionScanData(stops_per_id, footpaths_per_from_to_stop_id, trips_per_id)
    # TODO tests
