#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import date

from scripts.helpers.funs import parse_yymmdd, hhmmss_to_sec, seconds_to_hhmmssms

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