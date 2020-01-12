from builtins import id

from scripts.gtfs_parser import parse_gtfs


def test_gtfs_parser():
    path = "tests/resources/gtfsfp20192018-12-05_small.zip"
    cs_data = parse_gtfs(path)

    # stops
    assert 89 == len(cs_data.stops_per_id)
    def check_stop(stop_id, exp_code, exp_name, exp_easting, exp_northing):
        a_stop = cs_data.stops_per_id[stop_id]
        assert stop_id == a_stop.id
        assert exp_code == a_stop.code
        assert exp_name == a_stop.name
        assert exp_easting == a_stop.easting
        assert exp_northing == a_stop.northing
    
    check_stop("8500218:0:7","", "Olten", 7.90768978414808, 47.3522319182299)
    check_stop("8587654", "", "Glattbrugg, Glatthof", 8.56762812456551, 47.434511142518)
    check_stop("8594553","", "Opfikon, Schwimmbad", 8.57155376235766, 47.4326456250948)

    # footpaths
    assert 168 == len(cs_data.footpaths_per_from_to_stop_id)
    def check_footpath(from_stop_id, to_stop_id, exp_walking_time):
        a_footpath = cs_data.footpaths_per_from_to_stop_id[(from_stop_id, to_stop_id)]
        assert from_stop_id == a_footpath.from_stop_id
        assert to_stop_id == a_footpath.to_stop_id
        assert exp_walking_time == a_footpath.walking_time
    
    check_footpath("8500218:0:8", "8500218:0:7", 300)
    check_footpath("8503000:0:34", "8503000:0:14", 420)
    check_footpath("8501026:0:3", "8501026:0:1", 120)

