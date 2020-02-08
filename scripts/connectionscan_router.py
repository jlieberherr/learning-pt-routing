#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This module defines the core data structures for the implementation of the connection scan algorithm."""
import logging
from collections import defaultdict

from scripts.classes import Journey, Footpath
from scripts.helpers.funs import (hhmmss_to_sec, seconds_to_hhmmss)
from scripts.helpers.my_logging import log_end, log_start

log = logging.getLogger(__name__)


class ConnectionScanData:
    """Container for all timetable data.
    Designed so that the data can be used directly in the connection scan algorithm.

    Note that during the creation of an object various consistency checks are performed.
    For example all stop id's occurring in footpaths or connections of trips must also occur in stops_per_id.

    Args and attributes:
        stops_per_id (dict): stop per stop id.
        footpaths_per_from_to_stop_id (dict): footpath per (from_stop_id, to_stop_id)-tuple.
        trips_per_id (dict): trip per trip id.

    Additional attributes:
        stops_per_name (dict): stop per stop name. If the name is not unique, the name is assigned the best fitting stop
        according to the following logic: (1. stop which is a station, 2. stop which has the shortest id).
        sorted_connections (list): connections in the timetable sorted by departure time in the from stop.
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
            """Helper function for chosen the best fitting stop per stop name"""
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

        new_footpaths, footpaths_with_time_change = check_for_transitivity(self.footpaths_per_from_to_stop_id)
        if len(new_footpaths) > 0 or len(footpaths_with_time_change) > 0:
            msg_str = "footpaths are not transitive: there are {} missing footpaths and {} footpaths" \
                      " violating the triangle inequality"
            log.warning(msg_str.format(len(new_footpaths), len(footpaths_with_time_change)))

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
    """Container for the routing instance.

    Note that connection_scan_data.sorted_connections is a list and not an specific typed array.
    The performance when iterating over this list is therefore not optimal.

    Args and attributes:
        connection_scan_data (ConnectionScanData): timetable data belong to this routing instance.

    Additional attributes:
        stops_per_name (dict): stop per stop name. If the name is not unique, the name is assigned the best fitting stop
        according to the following logic: (1. stop which is a station, 2. stop which has the shortest id).
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

    def route_earliest_arrival(self, from_stop_id, to_stop_id, desired_dep_time):
        """Executes the unoptimized earliest arrival version (figure 3 of https://arxiv.org/pdf/1703.05997.pdf) of the
        connection scan algorithm from the source to the target stop respecting the desired departure time.

        Note:
            - In order to correctly model the footpaths at the start and end of the journey,
            the algorithm from the pseudo code is slightly modified.
            - the data structures are not optimized for performance.

        Args:
            from_stop_id (str): id of the source stop.
            to_stop_id (str): id of the target stop.
            desired_dep_time (int): desired departure time in seconds after midnight.

        Returns:
            int: earliest possible arrival time at the target stop.
        """

        log_start("unoptimized earliest arrival routing from {} to {} at {}".format(
            self.connection_scan_data.stops_per_id[from_stop_id].name,
            self.connection_scan_data.stops_per_id[to_stop_id].name,
            seconds_to_hhmmss(desired_dep_time)), log)

        # TODO implement task 1 here
        # Some hints:
        # - First get familiar with the data structures from the classes module and the ConnectionScanData class
        # - In order to correctly model the footpaths at the start and end of the journey,
        #   the algorithm from the pseudo code must be slightly modified.
        # - You could use the following dynamic data structures:
        #    - a dict for the earliest arrival including transfer/walking times per stop.
        #    - a int for the earliest arrival time at the target stop.
        #    - a dict to mark if a trip is set or not.

        res = -1
        log_end(additional_message="earliest arrival time: {}".format(seconds_to_hhmmss(res) if res else res))
        return res

    def route_earliest_arrival_with_reconstruction(self, from_stop_id, to_stop_id, desired_dep_time):
        """Executes the unoptimized earliest arrival with reconstruction version
        (figure 6 of https://arxiv.org/pdf/1703.05997.pdf) of the
        connection scan algorithm from the source to the target stop respecting the desired departure time.

        Note:
            - In order to correctly model the footpaths at the start and end of the journey,
            the algorithm from the pseudo code is slightly modified.
            - the data structures are not optimized for performance.

        Args:
            from_stop_id (str): id of the source stop.
            to_stop_id (str): id of the target stop.
            desired_dep_time (int): desired departure time in seconds after midnight.

        Returns:
            Journey: a Journey with earliest possible arrival time from the source to the target stop.
        """
        log_start("unoptimized earliest arrival routing with journey reconstruction from {} to {} at {}".format(
            self.connection_scan_data.stops_per_id[from_stop_id].name,
            self.connection_scan_data.stops_per_id[to_stop_id].name,
            seconds_to_hhmmss(desired_dep_time)), log)

        # TODO implement task 2 here
        # Some hints:
        # - Implement task 1 first.
        # - In order to correctly model the footpaths at the start and end of the journey,
        #   the algorithm from the pseudo code must be slightly modified.
        # - You could use the following dynamic data structures:
        #    - a dict for the earliest arrival including transfer/walking times per stop.
        #    - a int for the earliest arrival time at the target stop.
        #    - a dict for the in/boarding connection per trip.
        #    - a JourneyLeg for the last journey leg at the target stop.
        # - Construct the resulting Journey with the reconstruction logic from the pseudo code.

        res = Journey()
        log_end(additional_message="# journey legs: {}".format(0 if res is None else res.get_nb_journey_legs()))
        return res

    def route_optimized_earliest_arrival_with_reconstruction(self, from_stop_id, to_stop_id, desired_dep_time):
        """Executes the optimized earliest arrival with reconstruction version
        (figure 4 and 6 of https://arxiv.org/pdf/1703.05997.pdf) of the
        connection scan algorithm from the source to the target stop respecting the desired departure time.

        Note:
            - In order to correctly model the footpaths at the start and end of the journey,
            the algorithm from the pseudo code is slightly modified.
            - the data structures are not optimized for performance.

        Args:
            from_stop_id (str): id of the source stop.
            to_stop_id (str): id of the target stop.
            desired_dep_time (int): desired departure time in seconds after midnight.

        Returns:
            Journey: a Journey with earliest possible arrival time from the source to the target stop.
        """
        log_start("optimized earliest arrival routing with journey reconstruction from {} to {} at {}".format(
            self.connection_scan_data.stops_per_id[from_stop_id].name,
            self.connection_scan_data.stops_per_id[to_stop_id].name,
            seconds_to_hhmmss(desired_dep_time)), log)

        # TODO implement task 3 here
        # Some hints:
        # - Implement task 2 first.
        # - In order to correctly model the footpaths at the start and end of the journey,
        #   the algorithm from the pseudo code must be slightly modified.
        # - You could use the same dynamic data structures and reconstruction logic as in task 2.
        # - Implement the three optimization criterion's described in the paper (on page 8):
        #   stopping criterion, starting criterion and limited walking.
        #   For the starting criterion you can use the function binary_search from the funs module.

        res = Journey()
        log_end(additional_message="# journey legs: {}".format(0 if res is None else res.get_nb_journey_legs()))
        return res

    def route_by_name(self, from_stop_name, to_stop_name, desired_dep_time_hhmmss, router):
        """Wrapper function to execute routing requests based on the name of the source and target stop.

        Chooses the best fitting id for the source and target stop and forwards the routing request
        to the specified router.

        Args:
            from_stop_name (str): name of the source stop.
            to_stop_name (str): name of the target stop.
            desired_dep_time_hhmmss (str): time in format HH:MM:SS.
            router (Function): router to be called.

        Returns:
            The result of the request to the specified router.
        """
        return router(
            self.connection_scan_data.stops_per_name[from_stop_name].id,
            self.connection_scan_data.stops_per_name[to_stop_name].id,
            hhmmss_to_sec(desired_dep_time_hhmmss)
        )

    def route_earliest_arrival_by_name(self, from_stop_name, to_stop_name, desired_dep_time_hhmmss):
        """Wrapper function to execute unoptimized earliest arrival routing requests
         based on the name of the source and target stop.

        Chooses the best fitting id for the source and target stop and forwards the routing request
        to route_earliest_arrival.

        Args:
            from_stop_name (str): name of the source stop.
            to_stop_name (str): name of the target stop.
            desired_dep_time_hhmmss (str): time in format HH:MM:SS.

        Returns:
            int: earliest possible arrival at the target stop.
        """
        return self.route_by_name(
            from_stop_name,
            to_stop_name,
            desired_dep_time_hhmmss,
            self.route_earliest_arrival
        )

    def route_earliest_arrival_with_reconstruction_by_name(self, from_stop_name, to_stop_name, desired_dep_time_hhmmss):
        """Wrapper function to execute unoptimized earliest arrival routing with reconstruction requests
        based on the name of the source and target stop.

        Chooses the best fitting id for the source and target stop and forwards the routing request
        to route_earliest_arrival_with_reconstruction.

        Args:
            from_stop_name (str): name of the source stop.
            to_stop_name (str): name of the target stop.
            desired_dep_time_hhmmss (str): time in format HH:MM:SS.

        Returns:
            Journey: a Journey with earliest possible arrival time from the source to the target stop.
        """
        return self.route_by_name(
            from_stop_name,
            to_stop_name,
            desired_dep_time_hhmmss,
            self.route_earliest_arrival_with_reconstruction
        )

    def route_optimized_earliest_arrival_with_reconstruction_by_name(self, from_stop_name, to_stop_name,
                                                                     desired_dep_time_hhmmss):
        """Wrapper function to execute optimized earliest arrival routing with reconstruction requests
        based on the name of the source and target stop.

        Chooses the best fitting id for the source and target stop and forwards the routing request
        to route_optimized_earliest_arrival_with_reconstruction.

        Args:
            from_stop_name (str): name of the source stop.
            to_stop_name (str): name of the target stop.
            desired_dep_time_hhmmss (str): time in format HH:MM:SS.

        Returns:
            Journey: a Journey with earliest possible arrival time from the source to the target stop.
        """
        return self.route_by_name(
            from_stop_name,
            to_stop_name,
            desired_dep_time_hhmmss,
            self.route_optimized_earliest_arrival_with_reconstruction
        )


def check_for_transitivity(footpaths_per_from_to_stop_id):
    """Checks the footpaths for transitivity
    and returns missing footpaths and modified footpaths violating the triangle inequality.

    More precisely:
    - if there are three stops s_1, s_2 and s_3 with a footpath from s_1 to s_2 and a footpath from s_2 to s_3,
    but no footpath from s_1 to s_3, a new footpath from s_1 to s_3 is created (with walking time equal to the sum
    of the walking time of the two existing footpaths.
    This new footpath is added to the list returned in the first entry of the returned tuple.
    - if there are three stops s_1, s_2 and s_3 with a footpath from s_1 to s_2, s_2 to s_3 and s_1 to s_3, but the
    sum of the walking times of s_1 to s_2 and s_2 to s_3 is smaller than the walking time from s_1 to s_3,
    a new footpath from s_1 to s_3 is created with walking time equal to the sum of the two other walking times
    (only if this sum is positive).
    This new footpath is added to the list returned in the second entry of the returned tuple.

    Args:
        footpaths_per_from_to_stop_id (dict): footpath per (from_stop_id, to_stop_id)-tuple.

    Returns:
        tuple: new and modified footpaths (see above for the details).
    """
    log_start("checking footpaths for transitivity", log)
    footpaths_per_from_stop_id = {}
    for (from_stop_id, _), footpath in footpaths_per_from_to_stop_id.items():
        footpaths_per_from_stop_id[from_stop_id] = footpaths_per_from_stop_id.get(from_stop_id, []) + [footpath]
    new_footpaths = []
    footpaths_with_time_change = []
    footpaths_per_from_stop_id = dict(footpaths_per_from_stop_id)
    for from_stop_id, outgoing_footpaths in footpaths_per_from_stop_id.items():
        for first_footpath in outgoing_footpaths:
            for second_footpath in footpaths_per_from_stop_id.get(first_footpath.to_stop_id, []):
                second_to_stop_id = second_footpath.to_stop_id
                new_wt = first_footpath.walking_time + second_footpath.walking_time
                if (from_stop_id, second_to_stop_id) not in footpaths_per_from_to_stop_id:
                    new_footpaths += [Footpath(from_stop_id, second_to_stop_id, new_wt)]
                elif 0 < new_wt < footpaths_per_from_to_stop_id[(from_stop_id, second_to_stop_id)].walking_time:
                    footpaths_with_time_change += [Footpath(from_stop_id, second_to_stop_id, new_wt)]
    log_end()
    return new_footpaths, footpaths_with_time_change


def make_transitive(footpaths_per_from_to_stop_id):
    """Iteratively adds new footpaths or modifies the walking times until the footpaths are transitive.

    Args:
        footpaths_per_from_to_stop_id (dict): footpath per (from_stop_id, to_stop_id)-tuple.
    """
    log_start("making footpaths transitive", log)
    n = 0
    nb_footpaths_added = 0
    nb_footpaths_changed_time = 0
    while True:
        new_footpaths, footpaths_with_time_change = check_for_transitivity(footpaths_per_from_to_stop_id)
        if len(new_footpaths) > 0 or len(footpaths_with_time_change) > 0:
            for new_footpath in new_footpaths:
                footpaths_per_from_to_stop_id[new_footpath.from_stop_id, new_footpath.to_stop_id] = new_footpath
            for mod_footpath in footpaths_with_time_change:
                footpaths_per_from_to_stop_id[mod_footpath.from_stop_id, mod_footpath.to_stop_id] = mod_footpath
            str_msg = "iteration {}: # footpaths added: {}, # footpaths with changed walking time: {}"
            log.info(str_msg.format(n, len(new_footpaths), len(footpaths_with_time_change)))
            n += 1
            nb_footpaths_added += len(new_footpaths)
            nb_footpaths_changed_time += len(footpaths_with_time_change)
        else:
            break
    str_msg = "# iterations: {}, # footpaths added: {}, # footpaths with changed time: {}, # footpaths total: {}"
    log_end(additional_message=str_msg.format(
        n,
        nb_footpaths_added,
        nb_footpaths_changed_time,
        len(footpaths_per_from_to_stop_id))
    )
