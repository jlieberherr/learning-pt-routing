#!/usr/bin/python
# -*- coding: utf-8 -*-

import csv
import logging
from io import TextIOWrapper
from zipfile import ZipFile

import math
from pyproj import Transformer
from scipy import spatial

from scripts.classes import Connection, Footpath, Stop, Trip
from scripts.connectionscan_router import ConnectionScanData
from scripts.helpers.funs import hhmmss_to_sec, parse_yymmdd
from scripts.helpers.my_logging import log_end, log_start

ENCODING = "utf-8-sig"  # we use utf-8-sig since gtfs-data from switzerland are encoded in utf-8-with-bom

log = logging.getLogger(__name__)


def get_index_with_default(header, column_name, default_value=None):
    return header.index(column_name) if column_name in header else default_value


def parse_gtfs(
        path_to_gtfs_zip,
        desired_date,
        add_beeline_footpaths=True,
        beeline_distance=100.0,  # in meters
        walking_speed=2.0 / 3.6  # meters per second
):
    log_start("parsing gtfs-file for desired date {} ({})".format(desired_date, path_to_gtfs_zip), log)
    stops_per_id = {}
    footpaths_per_from_to_stop_id = {}
    trips_per_id = {}

    with ZipFile(path_to_gtfs_zip, "r") as zip_file:
        log_start("parsing stops.txt", log)
        with zip_file.open("stops.txt", "r") as gtfs_file:  # required
            reader = csv.reader(TextIOWrapper(gtfs_file, ENCODING))
            header = next(reader)
            id_index = header.index("stop_id")  # required
            code_index = get_index_with_default(header, "stop_code")  # optional
            name_index = get_index_with_default(header, "stop_name")  # conditionally required
            lat_index = get_index_with_default(header, "stop_lat")  # conditionally required
            lon_index = get_index_with_default(header, "stop_lon")  # conditionally required
            location_type_index = get_index_with_default(header, "location_type")
            parent_station_index = get_index_with_default(header, "parent_station")
            for row in reader:
                stop_id = row[id_index]
                is_station = row[location_type_index] == "1" if location_type_index else False
                parent_station_id = ((row[parent_station_index] if row[parent_station_index] != "" else None)
                                     if parent_station_index else None)
                stops_per_id[stop_id] = Stop(
                    stop_id,
                    row[code_index] if code_index else "",
                    row[name_index] if name_index else "",
                    float(row[lon_index]) if lon_index else 0.0,
                    float(row[lat_index]) if lat_index else 0.0,
                    is_station=is_station,
                    parent_station_id=parent_station_id
                )
        log_end(additional_message="# stops: {}".format(len(stops_per_id)))

        log_start("parsing transfers.txt", log)
        if "transfers.txt" in zip_file.namelist():
            with zip_file.open("transfers.txt", "r") as gtfs_file:  # optional
                reader = csv.reader(TextIOWrapper(gtfs_file, ENCODING))
                header = next(reader)
                from_stop_id_index = header.index("from_stop_id")  # required
                to_stop_id_index = header.index("to_stop_id")  # required
                transfer_type_index = header.index("transfer_type")  # required
                min_transfer_time_index = get_index_with_default(header, "min_transfer_time")  # optional
                if min_transfer_time_index:
                    nb_footpaths_not_added = 0
                    for row in reader:
                        if row[transfer_type_index] == "2":
                            from_stop_id = row[from_stop_id_index]
                            to_stop_id = row[to_stop_id_index]
                            if from_stop_id in stops_per_id and to_stop_id in stops_per_id:
                                footpaths_per_from_to_stop_id[(from_stop_id, to_stop_id)] = Footpath(
                                    from_stop_id,
                                    to_stop_id,
                                    int(row[min_transfer_time_index])
                                )
                            else:
                                nb_footpaths_not_added += 1
                                log.debug(("footpath from {} to {} cannot be defined since not both stops are defined "
                                           "in stops.txt").format(from_stop_id, to_stop_id))
                    if nb_footpaths_not_added > 0:
                        log.info(("{} rows from transfers.txt were not added to footpaths since either the "
                                  "from_stop_id or to_stop_id is not defined in stops.txt.").format(
                            nb_footpaths_not_added))
                else:
                    raise ValueError(("min_transfer_time column in gtfs transfers.txt file is not defined, "
                                      "cannot calculate footpaths."))
        log_end(additional_message="# footpaths from transfers.txt: {}".format(len(footpaths_per_from_to_stop_id)))
        log_start("adding footpaths to parent station", log)
        nb_parent_footpaths = 0
        for a_stop in stops_per_id.values():
            if a_stop.parent_station_id is not None:
                key = (a_stop.id, a_stop.parent_station_id)
                if key not in footpaths_per_from_to_stop_id:
                    footpaths_per_from_to_stop_id[key] = Footpath(key[0], key[1], 0)
                    nb_parent_footpaths += 1
                if (key[1], key[0]) not in footpaths_per_from_to_stop_id:
                    footpaths_per_from_to_stop_id[(key[1], key[0])] = Footpath(key[1], key[0], 0)
                    nb_parent_footpaths += 1
        log_end(additional_message="# footpath from/to parent_station added: {}. # footpaths total: {}".format(
            nb_parent_footpaths, len(footpaths_per_from_to_stop_id)))
        log_start("adding footpaths within stops (if not defined)", log)
        nb_loops = 0
        for stop_id in stops_per_id.keys():
            from_to_stop_id = (stop_id, stop_id)
            if from_to_stop_id not in footpaths_per_from_to_stop_id:
                footpaths_per_from_to_stop_id[from_to_stop_id] = Footpath(stop_id, stop_id, 0)  # best guess!!
                nb_loops += 1
        log_end(additional_message="# footpath loops added: {}, # footpaths total: {}".format(nb_loops, len(
            footpaths_per_from_to_stop_id)))

        if add_beeline_footpaths:
            create_beeline_footpaths(stops_per_id, footpaths_per_from_to_stop_id, beeline_distance, walking_speed)
        else:
            log.info("adding beeline footpaths is deactivated")

        log_start("parsing calendar.txt and calendar_dates.txt", log)
        service_available_at_date_per_service_id = get_service_available_at_date_per_service_id(zip_file, desired_date)
        log_end()

        log_start("parsing trips.txt", log)
        trip_available_at_date_per_trip_id = \
            get_trip_available_at_date_per_trip_id(zip_file, service_available_at_date_per_service_id)
        if len(trip_available_at_date_per_trip_id):
            msg = "# trips available at {}: {}".format(desired_date, len(trip_available_at_date_per_trip_id))
        else:
            msg = "no trips available at {}. assure that the date is within the timetable period.".format(desired_date)
        log_end(additional_message=msg)

        log_start("parsing stop_times.txt", log)
        with zip_file.open("stop_times.txt", "r") as gtfs_file:  # required
            reader = csv.reader(TextIOWrapper(gtfs_file, ENCODING))
            header = next(reader)
            trip_id_index = header.index("trip_id")  # required
            stop_id_index = header.index("stop_id")  # required
            arrival_time_index = get_index_with_default(header, "arrival_time")  # conditionally required
            departure_time_index = get_index_with_default(header, "departure_time")  # conditionally required

            def process_rows_of_trip(rows):
                if rows:
                    trip_id = rows[0][trip_id_index]
                    if trip_available_at_date_per_trip_id[trip_id]:
                        connections = []
                        for i in range(len(rows) - 1):
                            from_row = rows[i]
                            to_row = rows[i + 1]
                            con_dep = from_row[departure_time_index] if departure_time_index else None
                            con_arr = to_row[arrival_time_index] if arrival_time_index else None
                            if con_dep and con_arr:
                                connections += [Connection(
                                    trip_id,
                                    from_row[stop_id_index],
                                    to_row[stop_id_index],
                                    hhmmss_to_sec(con_dep),
                                    hhmmss_to_sec(con_arr))]
                            else:
                                return  # we do not want trips with missing times
                        trips_per_id[trip_id] = Trip(trip_id, connections)

            last_trip_id = None
            row_list = []
            for row in reader:
                act_trip_id = row[trip_id_index]
                if last_trip_id == act_trip_id:
                    row_list += [row]
                else:
                    process_rows_of_trip(row_list)
                    last_trip_id = act_trip_id
                    row_list = [row]
            process_rows_of_trip(row_list)
        log_end(additional_message="# trips: {}".format(len(trips_per_id)))

    cs_data = ConnectionScanData(stops_per_id, footpaths_per_from_to_stop_id, trips_per_id)
    log_end(additional_message="{}".format(cs_data))
    return cs_data


def get_service_available_at_date_per_service_id(zip_file, desired_date):
    service_available_at_date_per_service_id = {}
    # TODO handle that calendar.txt and calendar_dates.txt are only conditionally required
    with zip_file.open("calendar.txt", "r") as gtfs_file:  # conditionally required, but we assume that the file exists
        weekday_columns = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        reader = csv.reader(TextIOWrapper(gtfs_file, ENCODING))
        header = next(reader)
        service_id_index = header.index("service_id")  # required
        weekday_index = header.index(weekday_columns[desired_date.weekday()])  # required
        start_date_index = header.index("start_date")  # required
        end_date_index = header.index("end_date")  # required
        for row in reader:
            start_date = parse_yymmdd(row[start_date_index])
            end_date = parse_yymmdd(row[end_date_index])
            service_available_at_date_per_service_id[
                row[service_id_index]] = True if start_date <= desired_date <= end_date and row[
                weekday_index] == "1" else False

    with zip_file.open("calendar_dates.txt",
                       "r") as gtfs_file:  # conditionally required, but we assume that the file exists
        reader = csv.reader(TextIOWrapper(gtfs_file, ENCODING))
        header = next(reader)
        service_id_index = header.index("service_id")  # required
        date_index = header.index("date")  # required
        exception_type_index = header.index("exception_type")  # required
        for row in reader:
            service_id = row[service_id_index]
            date_ = parse_yymmdd(row[date_index])
            if date_ == desired_date:
                exception_type = row[exception_type_index]
                if exception_type == "1":
                    service_available_at_date_per_service_id[service_id] = True
                elif exception_type == "2":
                    service_available_at_date_per_service_id[service_id] = False
                else:
                    raise ValueError("as exception_type only 1 or 2 are permitted, but is: {}".format(exception_type))
    return service_available_at_date_per_service_id


def get_trip_available_at_date_per_trip_id(zip_file, service_available_at_date_per_service_id):
    trip_available_at_date_per_trip_id = {}
    with zip_file.open("trips.txt", "r") as gtfs_file:  # required
        reader = csv.reader(TextIOWrapper(gtfs_file, ENCODING))
        header = next(reader)
        trip_id_index = header.index("trip_id")  # required
        service_id_index = header.index("service_id")  # required
        for row in reader:
            trip_available_at_date_per_trip_id[row[trip_id_index]] = service_available_at_date_per_service_id[
                row[service_id_index]]
    return trip_available_at_date_per_trip_id


def create_beeline_footpaths(stops_per_id, footpaths_per_from_to_stop_id, beeline_distance, walking_speed):
    """
    adds beeline footpaths footpaths_per_from_to_stop_id from one stop to another 
    if there is no footpath already defined and the distance between them is <= beeline_distance.
    reason: in a lot of gtfs-files the transfers.txt data is not complete at all.
    """
    nb_footpaths_perimeter = 0
    log_start("adding footpaths in beeline perimeter with radius {}m".format(beeline_distance), log)
    # epsg:4326 is WGS84, epsg:4088 is world equidistant cylindrical (sphere)
    transformer = Transformer.from_proj(4326, 4088)
    log_start("transforming coordinates", log)
    stop_list = list(stops_per_id.values())
    easting_northing_list = [(s.easting, s.northing) for s in stop_list]
    x_y_coordinates = [transformer.transform(p[0], p[1]) for p in easting_northing_list]
    log_end()
    log_start("creating quadtree for fast perimeter search", log)
    tree = spatial.KDTree(x_y_coordinates)
    log_end()
    log_start("perimeter search around every stop", log)
    for ind, a_stop in enumerate(stop_list):
        x_y_a_stop = x_y_coordinates[ind]
        for another_ind in tree.query_ball_point(x_y_a_stop, beeline_distance):
            x_y_another_stop = x_y_coordinates[another_ind]
            distance = math.sqrt(sum([(a - b) ** 2 for a, b in zip(x_y_a_stop, x_y_another_stop)]))  # in meters
            walking_time = distance / walking_speed
            another_stop = stop_list[another_ind]
            key = (a_stop.id, another_stop.id)
            if key not in footpaths_per_from_to_stop_id:
                footpaths_per_from_to_stop_id[key] = Footpath(key[0], key[1], walking_time)
                nb_footpaths_perimeter += 1
            if (key[1], key[0]) not in footpaths_per_from_to_stop_id:
                footpaths_per_from_to_stop_id[(key[1], key[0])] = Footpath(key[1], key[0], walking_time)
                nb_footpaths_perimeter += 1
    log_end()
    log_end(additional_message="# footpath within perimeter added: {}. # footpaths total: {}".format(
        nb_footpaths_perimeter,
        len(footpaths_per_from_to_stop_id)
    ))
