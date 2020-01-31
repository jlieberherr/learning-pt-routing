#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This module defines some data structures for modeling public transport."""
from enum import Enum

from scripts.helpers.funs import seconds_to_hhmmss


class Stop:
    """Represents a stop (a station or platform) where trips can stop and passenger can board and alight.

    Args and attributes:
        stop_id (str): id of the stop.
        code (str): code of the stop.
        name (str): name of the stop
        easting (float): longitude of the stop in WGS84-coordinates.
        northing (float): latitude of the stop in WGS84-coordinates.
        is_station (:obj:`bool`, optional): is this stop a station. Default is False.
        parent_station_id (:obj:`str`, optional): stop id of the parent station, if exists, else None.
    """
    __slots__ = ["id", "code", "name", "easting", "northing", "is_station", "parent_station_id"]

    def __init__(self, stop_id, code, name, easting, northing, is_station=False, parent_station_id=None):
        self.id = stop_id
        self.code = code
        self.name = name
        self.easting = easting
        self.northing = northing
        self.is_station = is_station
        self.parent_station_id = parent_station_id

    def __str__(self):
        return "[id={}, code={}, name={}]".format(self.id, self.code, self.name)

    def __repr__(self):
        return str(self)


class Footpath:
    """Represents a footpath with a fixed walking time between two stops .
    Footpaths are used to model minimal transfer times for transfers between two trips
    (either within the same stop or between two different stops).

    Args and attributes:
        from_stop_id (str): id of the from stop.
        to_stop_id (str): id of the to stop.
        walking_time (int): walking time in seconds.
    """
    __slots__ = ["from_stop_id", "to_stop_id", "walking_time"]

    def __init__(self, from_stop_id, to_stop_id, walking_time):
        self.from_stop_id = from_stop_id
        self.to_stop_id = to_stop_id
        self.walking_time = walking_time

    def __str__(self):
        return "[from_stop_id={}, to_stop_id={}, walking_time={}]".format(self.from_stop_id, self.to_stop_id,
                                                                          self.walking_time)

    def __repr__(self):
        return str(self)


class Connection:
    """Represents a section of a trip between two stops.

    The departure time in the from stop must be before the arrival time in the to stop.

    Args and attributes:
        from_stop_id (str): id of the from stop.
        to_stop_id (str): id of the to stop.
        dep_time (int): departure time in from stop in seconds after midnight.
        arr_time (int): arrival time in to stop in seconds after midnight.
    """
    __slots__ = ["trip_id", "from_stop_id", "to_stop_id", "dep_time", "arr_time"]

    def __init__(self, trip_id, from_stop_id, to_stop_id, dep_time, arr_time):
        if dep_time > arr_time:
            raise ValueError("dep_time ({}) <= arr_time {} does not hold".format(dep_time, arr_time))
        self.trip_id = trip_id
        self.from_stop_id = from_stop_id
        self.to_stop_id = to_stop_id
        self.dep_time = dep_time
        self.arr_time = arr_time

    def __str__(self):
        return "[trip_id={}, from_stop_id={}, to_stop_id={}, dep_time={}, arr_time={}]".format(
            self.trip_id,
            self.from_stop_id,
            self.to_stop_id,
            seconds_to_hhmmss(self.dep_time),
            seconds_to_hhmmss(self.arr_time))

    def __repr__(self):
        return str(self)


class JourneyLeg:
    """A part of a journey on the same trip.

    The following cases are permitted:
    - only footpath: in_connection and out_connection are None, footpath is not None. This case can occur on
    the first journey leg of a journey (if the passenger walks from the source stop of the journey to another stop
    where he can board a trip).
    - full journey leg: in_connection and out_connection and footpath are not None. This is the standard case and can
    occur at any journey leg of a journey.
    - only public transport: in_connection and out_connection are not None, footpath is None. This case can occur on
    the last journey leg of a journey (if the target stop of the journey equals the to stop of the out_connection.

    Note that (if in_connection and out_connection are not None) the trip of the two connections must be the same.

    Args and attributes:
        in_connection (Connection): first connection of the journey leg.
        out_connection (Connection): last connection of the journey leg.
        footpath (Footpath): the footpath that follows the last connection.
    """
    __slots__ = ["in_connection", "out_connection", "footpath"]

    def __init__(self, in_connection, out_connection, footpath):
        if in_connection is None and out_connection is None and footpath is None:
            raise ValueError("either in_connection and out_connection or footpath or all three must be not None")
        if (in_connection is None and out_connection is not None) or (
                in_connection is not None and out_connection is None):
            raise ValueError(
                "in_connection {} and out_connection {} must both either be None or not None".format(in_connection,
                                                                                                     out_connection))
        if in_connection is not None and out_connection is not None:
            if in_connection.trip_id != out_connection.trip_id:
                raise ValueError("trip_id {} of in_connection is not equal to trip_id {} of out_connection.".format(
                    in_connection.trip_id, out_connection.trip_id))
            if in_connection != out_connection:
                if in_connection.dep_time > out_connection.arr_time:
                    raise ValueError("dep_time {} of in_connection is after arr_time {} of out_connection.".format(
                        seconds_to_hhmmss(in_connection.dep_time), seconds_to_hhmmss(out_connection.arr_time)))
        if footpath is not None and out_connection is not None:
            if out_connection.to_stop_id != footpath.from_stop_id:
                raise ValueError("to_stop_id {} of out_connection is not equal to from_stop_id {} of footpath".format(
                    out_connection.to_stop_id, footpath.from_stop_id))
        self.in_connection = in_connection
        self.out_connection = out_connection
        self.footpath = footpath

    def get_trip_id(self):
        """Returns the trip on which this journey leg takes place.

        Returns:
            int: trip_id of the trip if in_connection (and out_connection) is not None, else None.
        """
        if self.in_connection:
            return self.in_connection.trip_id
        else:
            return None

    def get_first_stop_id(self):
        """Returns the id of the first stop of the journey leg.

        Returns:
            int: id of the first stop, i.e. the id of the from stop of in_connection if in_connection is not None,
            else the id of the from stop of the footpath.
        """
        if self.in_connection is not None:
            return self.in_connection.from_stop_id
        else:
            return self.footpath.from_stop_id

    def get_last_stop_id(self):
        """Returns the id of the last stop of the journey leg.

        Returns:
            int: id of the last stop, i.e. the id of the to stop of the footpath if the footpath is not None,
            else the id of the to stop of the out_connection.
        """
        if self.footpath is not None:
            return self.footpath.to_stop_id
        else:
            return self.out_connection.to_stop_id

    def get_in_stop_id(self):
        """Returns the id of the stop where the passenger boards the trip of this connection.

        Returns:
            int: id of the from stop of in_connection if in_connection is not None, else None.
        """
        if self.in_connection is not None:
            return self.in_connection.from_stop_id
        else:
            return None

    def get_out_stop_id(self):
        """Returns the id of the stop where the passenger alights the trip of this connection.

        Returns:
            int: id of the to stop of out_connection if out_connection is not None, else None.
        """
        if self.out_connection is not None:
            return self.out_connection.to_stop_id
        else:
            return None

    def get_dep_time_in_stop_id(self):
        """Returns the departure time in the in stop in seconds after midnight.

        Returns:
            int: departure time in seconds after midnight of the in_connection if in_connection is not None, else None.
        """
        if self.in_connection is not None:
            return self.in_connection.dep_time
        else:
            return None

    def get_arr_time_out_stop_id(self):
        """Returns the arrival time in the out stop in seconds after midnight.

        Returns:
            int: arrival time in seconds after midnight of the out_connection if out_connection is not None, else None.
        """
        if self.out_connection is not None:
            return self.out_connection.arr_time
        else:
            return None

    def __str__(self):
        return "[trip_id={}, in_stop_id={}, out_stop_id={}, dep_time={}, arr_time={}]".format(
            self.get_trip_id(),
            self.get_in_stop_id(),
            self.get_out_stop_id(),
            seconds_to_hhmmss(self.get_dep_time_in_stop_id()),
            seconds_to_hhmmss(self.get_arr_time_out_stop_id())
        )

    def __repr__(self):
        return str(self)


class Journey:
    """Represents a journey from a source to a target stop,
    i.e. a list of journey legs consisting of connections and transfers in the public transport network.

    If you instantiate a journey the list of journey legs is emtpy.
    You build up the journey from target to source by
    inserting the journey legs in reverse order using prepend_journey_leg.

    Note that the journey must be consistent with respect to:
    - only the first journey leg can be of type "only footpath".
    - the last stop of a journey leg in the journey must equals the first stop of the subsequent journey leg.
    - the arrival time of a journey leg in the last stop cannot be after the departure time in the first stop
    of the subsequent journey leg.

    Attributes:
        journey_legs (list): list with the connections.
    """
    __slots__ = ["journey_legs"]

    def __init__(self):
        self.journey_legs = []

    def prepend_journey_leg(self, journey_leg):
        if self.has_legs():
            first_journey_leg_so_far = self.journey_legs[0]
            if journey_leg.in_connection is None and first_journey_leg_so_far.in_connection is None:
                raise ValueError("two subsequent journey legs without connections are not allowed")
            else:
                if journey_leg.get_last_stop_id() != self.get_first_stop_id():
                    raise ValueError(
                        "last_stop_id {} of new journey leg does not equal first_stop_id {} of actual journey".format(
                            journey_leg.get_last_stop_id(), self.get_first_stop_id()))
                else:
                    self.journey_legs = [journey_leg] + self.journey_legs
        else:
            self.journey_legs = [journey_leg]

    def get_nb_journey_legs(self):
        """Returns the number of journey legs.

        Returns:
            int: number of journey legs counting a journey leg of type "footpath only" as a full journey leg.
        """
        return len(self.journey_legs)

    def get_nb_pt_journey_legs(self):
        """Returns the number of journey legs using public transport.

        Returns:
            int: number of journey legs using public transport (i.e. where in_connection is not None).
        """
        return len([leg for leg in self.journey_legs if leg.in_connection is not None])

    def has_legs(self):
        """Returns True if the journey contains journey legs, else False.

        Returns:
            bool: True if the journey contains journey legs, else False.
        """
        return len(self.journey_legs) > 0

    def is_first_leg_footpath(self):
        """Returns True if the journey starts with a footpath.

        Returns:
            bool: True if in_connection of the first journey leg is None, else False
        """
        if self.has_legs():
            return True if self.journey_legs[0].in_connection is None else False
        else:
            return False

    def is_last_leg_footpath(self):
        """Returns True if the journey ends with a footpath.

        Returns:
            bool: True if footpath of last journey leg is not None, else False.
        """
        if self.has_legs():
            return True if self.journey_legs[-1].footpath is not None else False
        else:
            return False

    def get_first_stop_id(self):
        """Returns the id of the source stop, i.e. the first stop of the journey.

        Returns:
            int: id of the source stop.
        """
        if self.has_legs():
            first_journey_leg = self.journey_legs[0]
            if self.is_first_leg_footpath():
                return first_journey_leg.footpath.from_stop_id
            else:
                return first_journey_leg.in_connection.from_stop_id
        else:
            return None

    def get_last_stop_id(self):
        """Returns the id of the target stop, i.e. the last stop of the journey.

        Returns:
            int: id of the target stop.
        """
        if self.has_legs() > 0:
            last_journey_leg = self.journey_legs[-1]
            if self.is_last_leg_footpath():
                return last_journey_leg.footpath.to_stop_id
            else:
                return last_journey_leg.out_connection.to_stop_id
        else:
            return None

    def get_dep_time(self):
        """Returns the departure time of the journey in seconds after midnight.

        Returns:
            int: departure time in source stop of the journey in seconds after midnight if defined, else None.
        """
        if not self.has_legs():
            return None
        first_journey_leg = self.journey_legs[0]
        if first_journey_leg.in_connection is not None:
            return first_journey_leg.in_connection.dep_time
        else:
            if len(self.journey_legs) == 1:
                return None
            else:
                return self.journey_legs[1].in_connection.dep_time - first_journey_leg.footpath.walking_time

    def get_arr_time(self):
        """Returns the arrival time of the journey in seconds after midnight.

        Returns:
            int: arrival time in target stop of the journey in seconds after midnight if defined, else None.
        """
        if not self.has_legs():
            return None
        last_journey_leg = self.journey_legs[-1]
        if last_journey_leg.out_connection is not None:
            return last_journey_leg.out_connection.arr_time + (
                0 if last_journey_leg.footpath is None else last_journey_leg.footpath.walking_time)
        else:
            return None

    def get_pt_in_stop_ids(self):
        """Returns the list with the id's of the stops, where the passenger boards during the journey into trips.

        Returns:
            list: id's of the from stop's of the in_connection's of the journey.
        """
        return [journey_leg.in_connection.from_stop_id for journey_leg in self.journey_legs if
                journey_leg.in_connection is not None]

    def get_pt_out_stop_ids(self):
        """Returns the list with the id's of the stops, where the passenger alights during the journey into trips.

        Returns:
            list: id's of to stop's of the out_connection's of the journey.
        """
        return [journey_leg.out_connection.to_stop_id for journey_leg in self.journey_legs if
                journey_leg.out_connection is not None]

    def __str__(self):
        return "[journey_legs={}]".format(self.journey_legs)

    def __repr__(self):
        return str(self)


class TripType(Enum):
    """Definition of trip types"""
    TRAM = 0
    SUBWAY = 1
    RAIL = 2
    BUS = 3
    FERRY = 4
    CABLE_CAR = 5
    GONDOLA = 6
    FUNICULAR = 7
    UNKNOWN = 99


class Trip:
    """Represents a public transport vehicle which, according to defined times,
    drives through a sequence of stops where passengers can board or alight.

    Consists essentially of a consistent sequence of connections. Consistent means:
    - the to stop of a connection in the trip must equal the from stop in the subsequent connection.
    - the arrival time in the to stop of a connection in the trip
    must be <= the arrival time in the from stop of the subsequent connection.

    Args and attributes:
        trip_id (str): id of the trip.
        connections (list): list of connections.
        trip_type (obj:`TripType`, optional): type of the trip.
    """
    __slots__ = ["id", "connections", "trip_type"]

    def __init__(self, trip_id, connections, trip_type=TripType.UNKNOWN):
        self.id = trip_id
        for i in range(len(connections) - 1):
            act_con = connections[i]
            next_con = connections[i + 1]
            if act_con.to_stop_id != next_con.from_stop_id:
                raise ValueError(
                    "to_stop_id of connection {} does not equal from_stop_id of next connection {}".format(act_con,
                                                                                                           next_con))
            if act_con.arr_time > next_con.dep_time:
                raise ValueError(
                    "arr_time of connection {} is > than dep_time of next connection {}".format(act_con, next_con))
        self.connections = connections
        self.trip_type = trip_type

    def __str__(self):
        return ("[id={}, trip_type={}, first_stop_id={}, last_stop_id={}, dep_in_first_stop={}, "
                "arr_in_last_stop={}, #connections={}]").format(
            self.id,
            self.trip_type,
            self.connections[0].from_stop_id if self.connections else "",
            self.connections[-1].to_stop_id if self.connections else "",
            seconds_to_hhmmss(self.connections[0].dep_time) if self.connections else "",
            seconds_to_hhmmss(self.connections[-1].arr_time) if self.connections else "",
            len(self.connections))

    def __repr__(self):
        return str(self)

    def get_all_from_stop_ids(self):
        """Return a list with the id's of the stop's where passenger can board the trip.

        Returns:
            list: id's of the from stop's in the trip.
        """
        return [c.from_stop_id for c in self.connections]

    def get_all_to_stop_ids(self):
        """Return a list with the id's of the stop's where passenger can alight the trip.

        Returns:
            list: id's of the to stop's in the trip.
        """
        return [c.to_stop_id for c in self.connections]

    def get_set_of_all_stop_ids(self):
        """Returns the set of the id's of all served stop's.

        Returns:
            set: id's of the stop's in the trip.
        """
        return set(self.get_all_from_stop_ids()).union(set(self.get_all_to_stop_ids()))
