#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import date


def parse_yymmdd(yymmdd_str):
    y = int(yymmdd_str[:4])
    m = int(yymmdd_str[4:6])
    d = int(yymmdd_str[6:8])
    return date(y, m, d)


def hhmmss_to_sec(hhmmss):
    h, m, s = hhmmss.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)


def seconds_to_hhmmssms(seconds):
    int_seconds = int(seconds)
    ms = round((seconds - int_seconds) * 1000)
    m, s = divmod(int_seconds, 60)
    h, m = divmod(m, 60)
    return "{:02d}:{:02d}:{:02d}.{:03d}".format(h, m, s, ms)


def seconds_to_hhmmss(seconds):
    if seconds is None:
        return None
    int_seconds = int(seconds)
    m, s = divmod(int_seconds, 60)
    h, m = divmod(m, 60)
    return "{:02d}:{:02d}:{:02d}".format(h, m, s)


def binary_search(sorted_list, value, value_picker):
    """
    executes a binary search on sorted_list.
    returns the index of the first element in sorted_list which is <= value 
    or None if this element does not exist.
    value_picker defines the value of the elements in sorted_list.
    """
    n = len(sorted_list)

    def binary_search_recursive(from_index, to_index):
        if from_index > to_index or from_index >= n or to_index < 0:
            return None
        mid = (from_index + to_index) // 2
        if value_picker(sorted_list[mid]) < value:
            return binary_search_recursive(mid + 1, to_index)
        else:
            if mid == 0:
                return 0
            if value_picker(sorted_list[mid - 1]) < value:
                return mid
            else:
                return binary_search_recursive(from_index, mid - 1)

    return binary_search_recursive(0, n - 1)
