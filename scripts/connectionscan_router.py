#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import logging

log = logging.getLogger(__name__)

class ConnectionScanData:
    def __init__(self, stops_per_id, footpaths_per_from_to_stop_id, trips_per_id):
        log.info("start creating ConnectionScanData")
        start_time = time.time()
        # stops
        for stop_id, stop in stops_per_id.items():
            if stop_id != stop.id:
                raise ValueError("id in dict ({}) does not equal id in Stop {}".format(stop_id, stop))
        self.stops_per_id = stops_per_id

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
        log.info("end creating ConnectionScanData. time elapsed: {}".format(start_time - time.time()))
    
    def __str__(self):
        res = "ConnectionsScanData: "
        res += "# stops: {}, ".format(len(self.stops_per_id))
        res += "# footpaths: {}, ".format(len(self.footpaths_per_from_to_stop_id))
        res += "# trips: {}, ".format(len(self.trips_per_id))
        res += "# connections: {}".format(len(self.sorted_connections))
        return res

class ConnectionScanCore:
    def __init__(self, connection_scan_data):
        self.connection_scan_data = connection_scan_data
    
    def route(self, from_stop_id, to_stop_id, desired_dep_time):
        return None # TODO