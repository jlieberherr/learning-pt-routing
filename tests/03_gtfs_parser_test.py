from builtins import id
from datetime import date
from zipfile import ZipFile

from scripts.gtfs_parser import (get_service_available_at_date_per_service_id,
                                 parse_gtfs, parse_yymmdd)

PATH_GTFS_TEST_SAMPLE = "tests/resources/gtfsfp20192018-12-05_small.zip"

def test_parse_yymmdd():
    assert date(2020, 1, 12) == parse_yymmdd("20200112")
    assert date(2018, 12, 9) == parse_yymmdd("20181209")
    assert date(2019, 12, 14) == parse_yymmdd("20191214")


def test_gtfs_parser():
    cs_data = parse_gtfs(PATH_GTFS_TEST_SAMPLE, date(2019, 1, 18))

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


def test_get_service_available_at_date_per_service_id():
    with ZipFile(PATH_GTFS_TEST_SAMPLE, "r") as zip:
        service_abailable_at_date_per_service_id = get_service_available_at_date_per_service_id(zip, date(2019, 1, 18))
        # 2019-01-18 was a friday
        assert 46 == len(service_abailable_at_date_per_service_id)
        assert service_abailable_at_date_per_service_id["TA+b0001"]
        assert not service_abailable_at_date_per_service_id["TA+b02i1"]
        assert not service_abailable_at_date_per_service_id["TA+b00va"] # removed by calendar_dates.txt
        assert service_abailable_at_date_per_service_id["TA+b02ro"]
        assert not service_abailable_at_date_per_service_id["TA+b03ur"] # removed by calendar_dates.txt

