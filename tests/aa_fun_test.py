#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import date

from scripts.helpers.funs import parse_yymmdd, hhmmss_to_sec, seconds_to_hhmmssms, seconds_to_hhmmss, binary_search

def test_parse_yymmdd():
    assert date(2020, 1, 12) == parse_yymmdd("20200112")
    assert date(2018, 12, 9) == parse_yymmdd("20181209")
    assert date(2019, 12, 14) == parse_yymmdd("20191214")


def test_hhmmss_to_sec():
    assert 6 * 60 * 60 + 23 * 60 + 5== hhmmss_to_sec("06:23:05")

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


