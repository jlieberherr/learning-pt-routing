#!/usr/bin/python
# -*- coding: utf-8 -*-
import math
from datetime import date

from scripts.helpers.funs import parse_yymmdd, hhmmss_to_sec, seconds_to_hhmmssms, seconds_to_hhmmss, binary_search, \
    distance, wgs84_to_spherical_mercator


def test_parse_yymmdd():
    assert date(2020, 1, 12) == parse_yymmdd("20200112")
    assert date(2018, 12, 9) == parse_yymmdd("20181209")
    assert date(2019, 12, 14) == parse_yymmdd("20191214")


def test_hhmmss_to_sec():
    assert 6 * 60 * 60 + 23 * 60 + 5 == hhmmss_to_sec("06:23:05")


def test_seconds_to_hhmmssms():
    assert "00:00:00.013" == seconds_to_hhmmssms(0.012879)
    assert "00:00:02.012" == seconds_to_hhmmssms(2.012379)
    assert "03:05:02.112" == seconds_to_hhmmssms(3 * 60 * 60 + 5 * 60 + 2 + 0.112)


def test_seconds_to_hhmmss():
    assert "00:00:00" == seconds_to_hhmmss(0.012879)
    assert "00:00:02" == seconds_to_hhmmss(2.012379)
    assert "03:05:02" == seconds_to_hhmmss(3 * 60 * 60 + 5 * 60 + 2 + 0.112)
    assert "03:05:02" == seconds_to_hhmmss(3 * 60 * 60 + 5 * 60 + 2)


def test_binary_search():
    assert 2 == binary_search([2, 4, 5, 5, 5, 7, 8, 10, 10, 13], 5, lambda x: x)

    assert binary_search([2, 4, 5, 5, 5, 7, 8, 10, 10, 13], 20, lambda x: x) is None
    assert binary_search([2, 4, 5, 5, 5, 7, 8, 10, 10, 13], 14, lambda x: x) is None
    assert 9 == binary_search([2, 4, 5, 5, 5, 7, 8, 10, 10, 13], 13, lambda x: x)

    assert 0 == binary_search([2, 4, 5, 5, 5, 7, 8, 10, 10, 13], 2, lambda x: x)
    assert 0 == binary_search([2, 4, 5, 5, 5, 7, 8, 10, 10, 13], 1, lambda x: x)
    assert 0 == binary_search([2, 4, 5, 5, 5, 7, 8, 10, 10, 13], 0, lambda x: x)

    assert binary_search([], 2, lambda x: x) is None
    assert binary_search([1], 2, lambda x: x) is None
    assert 0 == binary_search([3], 2, lambda x: x)

    assert binary_search([2, 4, 5, 5, 7, 8, 10, 10, 13], 20, lambda x: x) is None
    assert 2 == binary_search([2, 4, 5, 5, 7, 8, 10, 10, 13], 5, lambda x: x)
    assert 1 == binary_search([2, 4, 5, 5, 7, 8, 10, 10, 13], 4, lambda x: x)
    assert 0 == binary_search([2, 2, 4, 5, 5, 7, 8, 10, 10, 13], 2, lambda x: x)
    assert 9 == binary_search([2, 2, 4, 5, 5, 7, 8, 10, 10, 13, 13], 13, lambda x: x)

    assert 0 == binary_search([2, 3], 2, lambda x: x)
    assert 0 == binary_search([2, 2], 2, lambda x: x)
    assert 1 == binary_search([2, 3], 3, lambda x: x)
    assert 1 == binary_search([2, 3, 3], 3, lambda x: x)


def test_distance():
    p = (2.0, 3.0)
    q = (3.0, -2.0)
    d = distance(p, q)
    assert d > math.sqrt(26) - 0.00001
    assert d < math.sqrt(26) + 0.00001


def test_wgs84_to_spherical_mercator_basel_zuerich():
    basel_sbb = (7.58955142623287, 47.5483160574667)
    zuerich_hb = (6.62909069062426, 47.3794536181612)
    wgs84_to_spherical_mercator_test(basel_sbb, zuerich_hb, 72000.0)


def test_wgs84_to_spherical_mercator_bern_bern_bahnhof():
    bern = (7.43911954873327, 46.9490702586521)
    bern_bahnhof = (7.44034125751985, 46.9484631542439)
    wgs84_to_spherical_mercator_test(bern, bern_bahnhof, 120.0)


def wgs84_to_spherical_mercator_test(lon_lat_1, lon_lat_2, exp_distance, tolerance_factor=2):
    coord_1 = wgs84_to_spherical_mercator(lon_lat_1[0], lon_lat_1[1])
    coord_2 = wgs84_to_spherical_mercator(lon_lat_2[0], lon_lat_2[1])
    d = distance(coord_1, coord_2)
    assert d > exp_distance / tolerance_factor
    assert d < exp_distance * tolerance_factor
