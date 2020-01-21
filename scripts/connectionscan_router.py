#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import time
from collections import defaultdict

from scripts.helpers.funs import seconds_to_hhmmss
from scripts.helpers.my_logging import log_end, log_start

log = logging.getLogger(__name__)

class ConnectionScanData:
    def __init__(self, stops_per_id, footpaths_per_from_to_stop_id, trips_per_id):
        log_start("creating ConnectionScanData", log)
        # stops
        for stop_id, stop in stops_per_id.items():
            if stop_id != stop.id:
                raise ValueError("id in dict ({}) does not equal id in Stop {}".format(stop_id, stop))
        self.stops_per_id = stops_per_id
        self.stops_per_name = {s.name: s for s in self.stops_per_id.values()}

        # footpaths
        for ((from_stop_id, to_stop_id), footpath) in footpaths_per_from_to_stop_id.items():
            if from_stop_id != footpath.from_stop_id:
                raise ValueError("from_stop_id {} in dict does not equal from_stop_id in footpath {}".format(from_stop_id, footpath))
            if to_stop_id != footpath.to_stop_id:
                raise ValueError("to_stop_id {} in dict does not equal to_stop_id in footpath {}".format(to_stop_id, footpath))
        
        stop_ids_in_footpaths = {s[0] for s in footpaths_per_from_to_stop_id.keys()}.union({s[1] for s in footpaths_per_from_to_stop_id.keys()})
        stop_ids_in_footpaths_not_in_stops = stop_ids_in_footpaths.difference(set(stops_per_id.keys()))
        if len(stop_ids_in_footpaths_not_in_stops) > 0:
            raise ValueError("there are stop_ids in footpaths_per_from_to_stop_id which do not accur as stop_id in stops_per_id: {}".format(stop_ids_in_footpaths_not_in_stops))

        self.footpaths_per_from_to_stop_id = footpaths_per_from_to_stop_id

        # trips
        for trip_id, trip in trips_per_id.items():
            if trip_id != trip.id:
                raise ValueError("id in dict ({}) does not equal id in Trip {}".format(trip_id, trip))
        
        stop_ids_in_trips = {s for t in trips_per_id.values() for s in t.get_set_of_all_stop_ids()}
        stop_ids_in_trips_not_in_stops = stop_ids_in_trips.difference(set(stops_per_id.keys()))
        if len(stop_ids_in_trips_not_in_stops) > 0:
            raise ValueError("there are stop_ids in trips_per_id which do not accur as stop_id in stops_per_id: {}".format(stop_ids_in_trips_not_in_stops))
        self.trips_per_id = trips_per_id

        cons_in_trips = [t.connections for t in trips_per_id.values()]
        self.sorted_connections = sorted([c for cons in cons_in_trips for c in cons], key=lambda c: (c.dep_time, c.arr_time))
        log_end()
    
    def __str__(self):
        res = "ConnectionsScanData: "
        res += "# stops: {}, ".format(len(self.stops_per_id))
        res += "# footpaths: {}, ".format(len(self.footpaths_per_from_to_stop_id))
        res += "# trips: {}, ".format(len(self.trips_per_id))
        res += "# connections: {}".format(len(self.sorted_connections))
        return res

class ConnectionScanCore:
    
    def __init__(self, connection_scan_data):
        log_start("creating ConnectionScanData", log)
        # static per ConnectionScanCore
        self.MAX_ARR_TIME_VALUE = 2 * 24 * 60 * 60 # we assume that arrival times are always within two days
        self.connection_scan_data = connection_scan_data
        self.incoming_footpaths_per_stop_id = defaultdict(list)
        for footpath in self.connection_scan_data.footpaths_per_from_to_stop_id.values():
            self.incoming_footpaths_per_stop_id[footpath.to_stop_id] += [footpath]
        log_end()

    
    def route(self, from_stop_id, to_stop_id, desired_dep_time):
        # this is a slightly modified version of the connection scan algorithm, footpaths are handled differently
        log_start("routing from {} to {} at {}".format(
            self.connection_scan_data.stops_per_id[from_stop_id].name, 
            self.connection_scan_data.stops_per_id[to_stop_id].name, 
            seconds_to_hhmmss(desired_dep_time)), log)

        # init dynamic data
        earliest_arrival_per_stop_id = {}
        trip_reached_per_trip_id = set()

        # init from_stop
        earliest_arrival_per_stop_id[from_stop_id] = desired_dep_time
        
        # scan connections
        for con in self.connection_scan_data.sorted_connections:
            if con.trip_id in trip_reached_per_trip_id:
                if con.arr_time < earliest_arrival_per_stop_id.get(con.to_stop_id, self.MAX_ARR_TIME_VALUE):
                    earliest_arrival_per_stop_id[con.to_stop_id] = con.arr_time
            else:
                for footpath in self.incoming_footpaths_per_stop_id[con.from_stop_id]:
                    time_to_add = 0 if from_stop_id == footpath.from_stop_id else footpath.walking_time
                    if earliest_arrival_per_stop_id.get(footpath.from_stop_id, self.MAX_ARR_TIME_VALUE) + time_to_add <= con.dep_time:
                        if con.arr_time < earliest_arrival_per_stop_id.get(con.to_stop_id, self.MAX_ARR_TIME_VALUE):
                            earliest_arrival_per_stop_id[con.to_stop_id] = con.arr_time
                            trip_reached_per_trip_id.add(con.trip_id)
        
        # iterate over incoming footpaths of to_stop
        for footpath in self.incoming_footpaths_per_stop_id[to_stop_id]:
            if earliest_arrival_per_stop_id.get(footpath.from_stop_id, self.MAX_ARR_TIME_VALUE) + footpath.walking_time < earliest_arrival_per_stop_id.get(to_stop_id, self.MAX_ARR_TIME_VALUE):
                earliest_arrival_per_stop_id[to_stop_id] = earliest_arrival_per_stop_id.get(footpath.from_stop_id, self.MAX_ARR_TIME_VALUE) + footpath.walking_time
        
        # return result
        ea = earliest_arrival_per_stop_id.get(to_stop_id, self.MAX_ARR_TIME_VALUE)
        res = None if ea == self.MAX_ARR_TIME_VALUE else ea
        log_end("earliest arrival time: {}".format(seconds_to_hhmmss(res) if res else res))
        return res
