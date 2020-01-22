#!/usr/bin/python
# -*- coding: utf-8 -*-

from scripts.classes import Connection, Footpath, Stop, Trip
from scripts.connectionscan_router import ConnectionScanData, ConnectionScanCore
from scripts.helpers.funs import seconds_to_hhmmss, hhmmss_to_sec

fribourg = Stop("1", "FR", "Fribourg/Freiburg", 0.0, 0.0)
bern = Stop("2", "BN", "Bern", 0.0, 0.0)
zuerich_hb = Stop("3", "ZUE", "Zürich HB", 0.0, 0.0)
winterthur = Stop("4", "W", "Winterthur", 0.0, 0.0)
st_gallen = Stop("5", "SG", "St. Gallen", 0.0, 0.0)
interlaken_ost = Stop("6", "IO", "Interlaken Ost", 0.0, 0.0)
basel_sbb = Stop("7", "BS", "Basel SBB", 0.0, 0.0)
chur = Stop("8", "CH", "Chur", 0.0, 0.0)
thusis = Stop("9", "TH", "Thusis", 0.0, 0.0)
samedan = Stop("10", "SAM", "Samedan", 0.0, 0.0)
st_moritz = Stop("11", "SM", "St. Moritz", 0.0, 0.0)
bern_duebystrasse = Stop("12", "", "Bern, Dübystrasse", 0.0, 0.0)
koenz_zentrum = Stop("13", "", "Köniz, Zentrum", 0.0, 0.0)
bern_bahnhof = Stop("14", "", "Bern, Bahnhof", 0.0, 0.0)
ostermundigen_bahnhof = Stop("15", "", "Ostermundigen, Bahnhof", 0.0, 0.0)
samedan_bahnhof = Stop("16", "", "Samedan, Bahnhof", 0.0, 0.0)
samedan_spital = Stop("17", "", "Samedan, Spital", 0.0, 0.0)

def create_test_connectionscan_data():

    stops_per_id = {s.id: s for s in [
        fribourg, 
        bern, 
        zuerich_hb, 
        winterthur, 
        st_gallen, 
        interlaken_ost, 
        basel_sbb, 
        chur, 
        thusis, 
        samedan, 
        st_moritz, 
        bern_duebystrasse, 
        koenz_zentrum,
        bern_bahnhof,
        ostermundigen_bahnhof,
        samedan_bahnhof,
        samedan_spital,
        ]}
    
    footpaths_per_from_stop_to_stop_id = {(s.id, s.id): Footpath(s.id, s.id, 2 * 60) for s in stops_per_id.values()}
    footpaths_per_from_stop_to_stop_id[(zuerich_hb.id, zuerich_hb.id)] = Footpath(zuerich_hb.id, zuerich_hb.id, 7 * 60)
    footpaths_per_from_stop_to_stop_id[(bern.id, bern.id)] =  Footpath(bern.id, bern.id, 5 * 60)
    footpaths_per_from_stop_to_stop_id[(bern_bahnhof.id, bern.id)] = Footpath(bern_bahnhof.id, bern.id, 5 * 60)
    footpaths_per_from_stop_to_stop_id[(bern.id, bern_bahnhof.id)] = Footpath(bern.id, bern_bahnhof.id, 5 * 60)
    footpaths_per_from_stop_to_stop_id[(chur.id, chur.id)] = Footpath(chur.id, chur.id, 4 * 60)
    footpaths_per_from_stop_to_stop_id[(samedan.id, samedan_bahnhof.id)] = Footpath(samedan.id, samedan_bahnhof.id, 3 * 60)
    footpaths_per_from_stop_to_stop_id[(samedan_bahnhof.id, samedan.id)] = Footpath(samedan_bahnhof.id, samedan.id, 3 * 60)

    trips = []

    trips += get_forth_and_back_trips(
        [fribourg, bern, zuerich_hb, winterthur, st_gallen],
        [22 * 60, 56 * 60, 26 * 60, 35 * 60],
        [6 * 60, 9 * 60, 3 * 60],
        hhmmss_to_sec("05:34:00"),
        32,
        30 * 60
    )

    trips += get_forth_and_back_trips(
        [interlaken_ost, bern, basel_sbb],
        [52 * 60, 55 * 60],
        [12 * 60],
        hhmmss_to_sec("05:00:00"),
        16,
        60 * 60
    )

    trips += get_forth_and_back_trips(
        [basel_sbb, zuerich_hb, chur],
        [53 * 60, 75 * 60],
        [11 * 60],
        hhmmss_to_sec("05:33:00"),
        16,
        60 * 60
    )

    trips += get_forth_and_back_trips(
        [chur, thusis, samedan, st_moritz],
        [30 * 60, 75 * 60, 12 * 60], 
        [2 * 60, 6 * 60],
        hhmmss_to_sec("05:58:00"),
        16,
        60 * 60
    )

    trips += get_forth_and_back_trips(
        [koenz_zentrum, bern_duebystrasse, bern_bahnhof, ostermundigen_bahnhof],
        [6 * 60, 7 * 60, 15 * 60],
        [0, 0],
        hhmmss_to_sec("05:00:00"),
        10 * 16,
        6 * 60
    )

    trips += get_forth_and_back_trips(
        [samedan_bahnhof, samedan_spital],
        [7 * 60],
        [],
        hhmmss_to_sec("15:00:00"),
        1,
        24 * 60 * 60
    )
    return ConnectionScanData(stops_per_id, footpaths_per_from_stop_to_stop_id, {t.id: t for t in trips})


def create_trips(stops, running_times, stop_times, first_departure, nb_trips, headway):
    trips = []
    for trip_index in range(nb_trips):
        dep_first_stop = first_departure + trip_index * headway
        trip_id = "{}_{}_{}_{}".format(stops[0].name, stops[-1].name, seconds_to_hhmmss(dep_first_stop), trip_index)
        cons = []
        for stop_index in range(len(stops) - 1):
            dep = dep_first_stop if stop_index == 0 else arr + stop_times[stop_index - 1]
            arr = dep + running_times[stop_index]
            cons += [Connection(trip_id, stops[stop_index].id, stops[stop_index + 1].id, dep, arr)]
        trips += [Trip(trip_id, cons)]
    return trips

def test_create_trips():
    dep_first_trip_first_stop = 5 * 60 * 60 + 42 * 60
    trips_fri_sg = create_trips(
        [fribourg, bern, zuerich_hb, winterthur, st_gallen], 
        [14 * 60, 58 * 60, 20 * 60, 38 * 60],
        [6 * 60, 5 * 60, 3 * 60], 
        dep_first_trip_first_stop,
        32,
        30 * 60)
    assert len(trips_fri_sg) == 32
    assert "1" == trips_fri_sg[3].connections[0].from_stop_id
    assert "2" == trips_fri_sg[3].connections[0].to_stop_id
    assert "2" == trips_fri_sg[3].connections[1].from_stop_id
    assert "3" == trips_fri_sg[3].connections[1].to_stop_id
    assert "4" == trips_fri_sg[3].connections[-1].from_stop_id
    assert "5" == trips_fri_sg[3].connections[-1].to_stop_id


    assert "08:12:00" == seconds_to_hhmmss(trips_fri_sg[5].connections[0].dep_time)
    assert "08:26:00" == seconds_to_hhmmss(trips_fri_sg[5].connections[0].arr_time)
    assert "08:32:00" == seconds_to_hhmmss(trips_fri_sg[5].connections[1].dep_time)
    assert "09:30:00" == seconds_to_hhmmss(trips_fri_sg[5].connections[1].arr_time)
    assert "09:35:00" == seconds_to_hhmmss(trips_fri_sg[5].connections[2].dep_time)
    assert "09:55:00" == seconds_to_hhmmss(trips_fri_sg[5].connections[2].arr_time)
    assert "09:58:00" == seconds_to_hhmmss(trips_fri_sg[5].connections[3].dep_time)
    assert "10:36:00" == seconds_to_hhmmss(trips_fri_sg[5].connections[3].arr_time)

def get_forth_and_back_trips(stops, running_times, stop_times, dep_first_trip, nb_trips, headway):
    return create_trips(
        stops, 
        running_times, 
        stop_times, 
        dep_first_trip, 
        nb_trips, 
        headway) + create_trips(
            list(reversed(stops)),
            list(reversed(running_times)),
            list(reversed(stop_times)),
            dep_first_trip,
            nb_trips,
            headway)

def test_get_forth_and_back_trips():
    dep_first_trip_first_stop = 5 * 60 * 60 + 42 * 60
    trips = get_forth_and_back_trips(
        [fribourg, bern, zuerich_hb, winterthur, st_gallen], 
        [14 * 60, 58 * 60, 20 * 60, 38 * 60],
        [6 * 60, 5 * 60, 3 * 60], 
        dep_first_trip_first_stop,
        32,
        30 * 60)
    assert len(trips) == 64
    trips_fri_sg = trips[:32]
    trips_sg_fri = trips[32:65]
    assert "1" == trips_fri_sg[0].connections[0].from_stop_id
    assert "5" == trips_fri_sg[-1].connections[-1].to_stop_id

    assert "5" == trips_sg_fri[0].connections[0].from_stop_id
    assert "1" == trips_sg_fri[-1].connections[-1].to_stop_id

def test_bern_zuerich_hb_earliest_arrivals():
    cs_data = create_test_connectionscan_data()
    cs_core = ConnectionScanCore(cs_data)
    assert "08:58:00" == seconds_to_hhmmss(cs_core.route(bern.id, zuerich_hb.id, hhmmss_to_sec("07:35:00")))
    assert "08:58:00" == seconds_to_hhmmss(cs_core.route(bern.id, zuerich_hb.id, hhmmss_to_sec("08:02:00")))
    assert None == cs_core.route(bern.id, zuerich_hb.id, hhmmss_to_sec("23:33:00"))

def test_bern_samedan_earliest_arrivals():
    cs_data = create_test_connectionscan_data()
    cs_core = ConnectionScanCore(cs_data)
    assert "12:45:00" == seconds_to_hhmmss(cs_core.route(bern.id, samedan.id, hhmmss_to_sec("08:30:00")))
    assert None == cs_core.route(bern.id, samedan.id, hhmmss_to_sec("21:00:00"))

def test_bern_samedan_spital_earliest_arrivals():
    cs_data = create_test_connectionscan_data()
    cs_core = ConnectionScanCore(cs_data)
    assert "15:07:00" == seconds_to_hhmmss(cs_core.route(bern.id, samedan_spital.id, hhmmss_to_sec("07:30:00")))

def test_bern_duebystrasse_samedan_earliest_arrivals():
    cs_data = create_test_connectionscan_data()
    cs_core = ConnectionScanCore(cs_data)
    assert "12:45:00" == seconds_to_hhmmss(cs_core.route(bern_duebystrasse.id, samedan.id, hhmmss_to_sec("07:30:00")))

def test_basel_st_gallen_earliest_arrivals():
    cs_data = create_test_connectionscan_data()
    cs_core = ConnectionScanCore(cs_data)
    assert "09:41:00" == seconds_to_hhmmss(cs_core.route(basel_sbb.id, st_gallen.id, hhmmss_to_sec("07:30:00")))

def test_bern_duebystrasse_ostermundigen_bahnhof():
    cs_data = create_test_connectionscan_data()
    cs_core = ConnectionScanCore(cs_data)
    assert "12:34:00" == seconds_to_hhmmss(cs_core.route(bern_duebystrasse.id, ostermundigen_bahnhof.id, hhmmss_to_sec("12:09:46")))

def test_bern_bern():
    cs_data = create_test_connectionscan_data()
    cs_core = ConnectionScanCore(cs_data)
    assert "12:09:46" == seconds_to_hhmmss(cs_core.route(bern.id, bern.id, hhmmss_to_sec("12:09:46")))

def test_bern_bern_bahnhof():
    cs_data = create_test_connectionscan_data()
    cs_core = ConnectionScanCore(cs_data)
    assert "12:14:46" == seconds_to_hhmmss(cs_core.route(bern.id, bern_bahnhof.id, hhmmss_to_sec("12:09:46")))
