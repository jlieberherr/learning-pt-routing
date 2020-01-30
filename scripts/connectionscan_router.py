#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from collections import defaultdict

from scripts.classes import Journey
from scripts.helpers.funs import (hhmmss_to_sec,
                                  seconds_to_hhmmss)
from scripts.helpers.my_logging import log_end, log_start

log = logging.getLogger(__name__)


class ConnectionScanData:
    """
    container for all timetable data.
    structured so that you can use it directly in the core routing algorithm.
    """
    def __init__(self, stops_per_id, footpaths_per_from_to_stop_id, trips_per_id):
        log_start("creating ConnectionScanData", log)
        # stops
        for stop_id, stop in stops_per_id.items():
            if stop_id != stop.id:
                raise ValueError("id in dict ({}) does not equal id in Stop {}".format(stop_id, stop))
        self.stops_per_id = stops_per_id
        stop_list_per_name = defaultdict(list)
        for a_stop in self.stops_per_id.values():
            stop_list_per_name[a_stop.name] += [a_stop]

        def choose_best_stop(stops_with_same_name):
            stops_with_same_name_sorted = sorted(stops_with_same_name,
                                                 key=lambda s: (0 if s.is_station else 1, len(s.id)))
            return stops_with_same_name_sorted[0]

        self.stops_per_name = {name: choose_best_stop(stop_list) for (name, stop_list) in stop_list_per_name.items()}

        # footpaths
        for ((from_stop_id, to_stop_id), footpath) in footpaths_per_from_to_stop_id.items():
            if from_stop_id != footpath.from_stop_id:
                raise ValueError(
                    "from_stop_id {} in dict does not equal from_stop_id in footpath {}".format(from_stop_id, footpath))
            if to_stop_id != footpath.to_stop_id:
                raise ValueError(
                    "to_stop_id {} in dict does not equal to_stop_id in footpath {}".format(to_stop_id, footpath))

        stop_ids_in_footpaths = {s[0] for s in footpaths_per_from_to_stop_id.keys()}.union(
            {s[1] for s in footpaths_per_from_to_stop_id.keys()})
        stop_ids_in_footpaths_not_in_stops = stop_ids_in_footpaths.difference(set(stops_per_id.keys()))
        if len(stop_ids_in_footpaths_not_in_stops) > 0:
            raise ValueError(("there are stop_ids in footpaths_per_from_to_stop_id which do not occur as stop_id in "
                              "stops_per_id: {}").format(
                stop_ids_in_footpaths_not_in_stops))

        self.footpaths_per_from_to_stop_id = footpaths_per_from_to_stop_id

        # trips
        for trip_id, trip in trips_per_id.items():
            if trip_id != trip.id:
                raise ValueError("id in dict ({}) does not equal id in Trip {}".format(trip_id, trip))

        stop_ids_in_trips = {s for t in trips_per_id.values() for s in t.get_set_of_all_stop_ids()}
        stop_ids_in_trips_not_in_stops = stop_ids_in_trips.difference(set(stops_per_id.keys()))
        if len(stop_ids_in_trips_not_in_stops) > 0:
            raise ValueError(
                "there are stop_ids in trips_per_id which do not occur as stop_id in stops_per_id: {}".format(
                    stop_ids_in_trips_not_in_stops))
        self.trips_per_id = trips_per_id

        cons_in_trips = [t.connections for t in trips_per_id.values()]
        self.sorted_connections = sorted([c for cons in cons_in_trips for c in cons],
                                         key=lambda c: (c.dep_time, c.arr_time))
        log_end()

    def __str__(self):
        res = "ConnectionsScanData: "
        res += "# stops: {}, ".format(len(self.stops_per_id))
        res += "# footpaths: {}, ".format(len(self.footpaths_per_from_to_stop_id))
        res += "# trips: {}, ".format(len(self.trips_per_id))
        res += "# connections: {}".format(len(self.sorted_connections))
        return res


class ConnectionScanCore:
    """
    core container, in which you implement the routing algorithm (task 1, 2 and 3)
    """
    def __init__(self, connection_scan_data):
        log_start("creating ConnectionScanData", log)
        # static per ConnectionScanCore
        self.MAX_ARR_TIME_VALUE = 2 * 24 * 60 * 60  # we assume that arrival times are always within two days
        self.connection_scan_data = connection_scan_data
        self.outgoing_footpaths_per_stop_id = defaultdict(list)
        for footpath in self.connection_scan_data.footpaths_per_from_to_stop_id.values():
            self.outgoing_footpaths_per_stop_id[footpath.from_stop_id] += [footpath]
        log_end()

    def route_by_name(self, from_stop_name, to_stop_name, desired_dep_time_hhmmss, router):
        return router(
            self.connection_scan_data.stops_per_name[from_stop_name].id,
            self.connection_scan_data.stops_per_name[to_stop_name].id,
            hhmmss_to_sec(desired_dep_time_hhmmss)
        )

    def route_earliest_arrival_by_name(self, from_stop_name, to_stop_name, desired_dep_time_hhmmss):
        return self.route_by_name(
            from_stop_name,
            to_stop_name,
            desired_dep_time_hhmmss,
            self.route_earliest_arrival
        )

    def route_earliest_arrival_with_reconstruction_by_name(self, from_stop_name, to_stop_name, desired_dep_time_hhmmss):
        return self.route_by_name(
            from_stop_name,
            to_stop_name,
            desired_dep_time_hhmmss,
            self.route_earliest_arrival_with_reconstruction
        )

    def route_optimized_earliest_arrival_with_reconstruction_by_name(self, from_stop_name, to_stop_name,
                                                                     desired_dep_time_hhmmss):
        return self.route_by_name(
            from_stop_name,
            to_stop_name,
            desired_dep_time_hhmmss,
            self.route_optimized_earliest_arrival_with_reconstruction
        )

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

        # TODO implement task 1 here
        # some hints for your implementation:
        # - use the data structures prepared in scripts.classes and ConnectionScanData
        # - TODO

        res = None
        log_end(additional_message="earliest arrival time: {}".format(seconds_to_hhmmss(res) if res else res))
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

        # TODO implement task 2 here

        res = Journey()
        log_end(additional_message="# journey legs: {}".format(0 if res is None else res.get_nb_journey_legs()))
        return res

    def route_optimized_earliest_arrival_with_reconstruction(self, from_stop_id, to_stop_id, desired_dep_time):
        """
        slightly modified version of optimized earliest-arrival routing with journey reconstruction
        with the connection scan algorithm presented in figure 4 and 6 of https://arxiv.org/pdf/1703.05997.pdf.
        note that the data structures are not optimized for performance.
        """
        log_start("optimized earliest arrival routing with journey reconstruction from {} to {} at {}".format(
            self.connection_scan_data.stops_per_id[from_stop_id].name,
            self.connection_scan_data.stops_per_id[to_stop_id].name,
            seconds_to_hhmmss(desired_dep_time)), log)

        # TODO implement task 3 here

        res = Journey()
        log_end(additional_message="# journey legs: {}".format(0 if res is None else res.get_nb_journey_legs()))
        return res
