#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import time
from collections import defaultdict

from scripts.helpers.funs import seconds_to_hhmmss
from scripts.helpers.my_logging import log_end, log_start
from scripts.classes import JourneyLeg, Journey

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
        self.outgoing_footpaths_per_stop_id = defaultdict(list)
        for footpath in self.connection_scan_data.footpaths_per_from_to_stop_id.values():
            self.outgoing_footpaths_per_stop_id[footpath.from_stop_id] += [footpath]
        log_end()

    
    def route_earliest_arrival(self, from_stop_id, to_stop_id, desired_dep_time):
        """
        slightly modified version of unoptimized earliest-arrival routing
        with the connection scan algorithm presented in figure 3 of https://arxiv.org/pdf/1703.05997.pdf.
        note that the data structures are not optimized for performance.
        """
        log_start("unoptimized earliest arrival routing from {} to {} at {}".format(
            self.connection_scan_data.stops_per_id[from_stop_id].name, 
            self.connection_scan_data.stops_per_id[to_stop_id].name, 
            seconds_to_hhmmss(desired_dep_time)), log)

        # init dynamic data
        earliest_arrival_including_transfer_time_per_stop_id = {}
        earliest_arrival_at_target = self.MAX_ARR_TIME_VALUE # additional to the original algorithm (helps to handle footpaths in a more consistent way)
        trip_reached_per_trip_id = set()

        # init from_stop
        for footpath in self.outgoing_footpaths_per_stop_id[from_stop_id]:
            arr_time = desired_dep_time + (0 if footpath.from_stop_id == footpath.to_stop_id else footpath.walking_time)
            # add walking time only if footpath is not a loop
            earliest_arrival_including_transfer_time_per_stop_id[footpath.to_stop_id] =  arr_time
            if footpath.to_stop_id == to_stop_id and arr_time < earliest_arrival_at_target:
                # handle earliest_arrival_at_target seperately (we do not want to add a walking time if it is not necessary)
                earliest_arrival_at_target = arr_time
        
        # scan connections
        for con in self.connection_scan_data.sorted_connections:
            if con.trip_id in trip_reached_per_trip_id or earliest_arrival_including_transfer_time_per_stop_id.get(con.from_stop_id, self.MAX_ARR_TIME_VALUE) <= con.dep_time:
                trip_reached_per_trip_id.add(con.trip_id)
                for footpath in self.outgoing_footpaths_per_stop_id[con.to_stop_id]:
                    if con.arr_time + footpath.walking_time < earliest_arrival_including_transfer_time_per_stop_id.get(footpath.to_stop_id, self.MAX_ARR_TIME_VALUE):
                        earliest_arrival_including_transfer_time_per_stop_id[footpath.to_stop_id] = con.arr_time + footpath.walking_time
                    if footpath.to_stop_id == to_stop_id:
                        # handle earliest_arrival_at_target seperately (we do not want to add a walking time if it is not necessary)
                        arr_time = con.arr_time + (0 if footpath.from_stop_id == footpath.to_stop_id else footpath.walking_time)
                        if arr_time < earliest_arrival_at_target:
                            earliest_arrival_at_target = arr_time
        
        # return result
        res = None if earliest_arrival_at_target == self.MAX_ARR_TIME_VALUE else earliest_arrival_at_target
        log_end("earliest arrival time: {}".format(seconds_to_hhmmss(res) if res else res))
        return res
    
    def route_earliest_arrival_with_reconstruction(self, from_stop_id, to_stop_id, desired_dep_time):
        """
        slightly modified version of unoptimized earliest-arrival routing with journey reconstruction
        with the connection scan algorithm presented in figure 6 of https://arxiv.org/pdf/1703.05997.pdf.
        note that the data structures are not optimized for performance.
        """
        log_start("unoptimized earliest arrival routing with journey reconstruction from {} to {} at {}".format(
            self.connection_scan_data.stops_per_id[from_stop_id].name, 
            self.connection_scan_data.stops_per_id[to_stop_id].name, 
            seconds_to_hhmmss(desired_dep_time)), log)

        if from_stop_id == to_stop_id:
            return Journey()

        # init dynamic data
        earliest_arrival_including_transfer_time_per_stop_id = {}
        earliest_arrival_at_target = self.MAX_ARR_TIME_VALUE # additional to the original algorithm (helps to handle footpaths in a more consistent way)
        in_connection_per_trip_id = {}
        last_journey_leg_per_stop_id = {}
        last_journey_leg_at_target = None

        # init from_stop
        for footpath in self.outgoing_footpaths_per_stop_id[from_stop_id]:
            arr_time = desired_dep_time + (0 if footpath.from_stop_id == footpath.to_stop_id else footpath.walking_time)
            # add walking time only if footpath is not a loop
            earliest_arrival_including_transfer_time_per_stop_id[footpath.to_stop_id] =  arr_time
            if footpath.to_stop_id == to_stop_id and arr_time < earliest_arrival_at_target:
                # handle earliest_arrival_at_target seperately (we do not want to add a walking time if it is not necessary)
                earliest_arrival_at_target = arr_time
        
        # scan connections
        for con in self.connection_scan_data.sorted_connections:
            in_connection = in_connection_per_trip_id.get(con.trip_id, None)
            if in_connection is not None or earliest_arrival_including_transfer_time_per_stop_id.get(con.from_stop_id, self.MAX_ARR_TIME_VALUE) <= con.dep_time:
                if in_connection is None:
                    in_connection_per_trip_id[con.trip_id] = con
                for footpath in self.outgoing_footpaths_per_stop_id[con.to_stop_id]:
                    if con.arr_time + footpath.walking_time < earliest_arrival_including_transfer_time_per_stop_id.get(footpath.to_stop_id, self.MAX_ARR_TIME_VALUE):
                        earliest_arrival_including_transfer_time_per_stop_id[footpath.to_stop_id] = con.arr_time + footpath.walking_time
                        last_journey_leg_per_stop_id[footpath.to_stop_id] = JourneyLeg(in_connection_per_trip_id[con.trip_id], con, footpath)
                    if footpath.to_stop_id == to_stop_id:
                        # handle earliest_arrival_at_target seperately (we do not want to add a walking time if it is not necessary)
                        arr_time = con.arr_time + (0 if footpath.from_stop_id == footpath.to_stop_id else footpath.walking_time)
                        if arr_time < earliest_arrival_at_target:
                            earliest_arrival_at_target = arr_time
                            last_footpath = None if footpath.from_stop_id == footpath.to_stop_id else footpath
                            last_journey_leg_at_target = JourneyLeg(in_connection_per_trip_id[con.trip_id], con, last_footpath)
        
        # reconstruct journey
        last_journey_leg_per_stop_id[to_stop_id] = last_journey_leg_at_target
        journey = Journey()
        act_stop_id = to_stop_id
        while last_journey_leg_per_stop_id.get(act_stop_id, None) is not None:
            journey.prepend_journey_leg(last_journey_leg_per_stop_id[act_stop_id])
            act_stop_id = last_journey_leg_per_stop_id[act_stop_id].in_connection.from_stop_id
        
        if from_stop_id == act_stop_id:
            res = journey
        elif (from_stop_id, act_stop_id) in self.connection_scan_data.footpaths_per_from_to_stop_id:
            journey.prepend_journey_leg(JourneyLeg(None, None, self.connection_scan_data.footpaths_per_from_to_stop_id[(from_stop_id, act_stop_id)]))
            res = journey
        else:
            res = None
        log_end("journey: {}".format(res))
        return res
