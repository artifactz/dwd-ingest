import time
from datetime import datetime
import fetch, db
from dump_progress import dump_progress


def run(interval_seconds=60):
    while True:
        unknown_stations, short_update_stations, long_update_stations = determine_stations()

        update_stations(unknown_stations)

        if update_longterm_measurements(list(long_update_stations.keys())):
            # This takes ~1h, so previous data from determine_stations() is outdated at this point
            continue

        update_shortterm_measurements(short_update_stations)

        if not unknown_stations and not short_update_stations and not long_update_stations:
            print("No updates.")

        time.sleep(interval_seconds)


def determine_stations() -> tuple[list[int], dict[int, datetime], dict[int, datetime]]:
    timestamps = fetch.temperature_published_timestamps("now")
    unknown_stations = []
    short_update_stations = {}
    long_update_stations = {}

    for station_id, published_online in timestamps.items():

        if not db.has_station(station_id):
            unknown_stations.append(station_id)

        published_db = db.get_latest_publish_time(station_id)
        if (
            published_db is None or published_online.year > published_db.year or
            published_online.month > published_db.month or published_online.day > published_db.day
        ):
            # First time fetching this station or last fetch was on another day
            long_update_stations[station_id] = published_online
        elif published_online > published_db:
            short_update_stations[station_id] = published_online

    return unknown_stations, short_update_stations, long_update_stations


def update_stations(station_ids: list[int]):
    if not station_ids:
        return

    print(f"Discovered {len(station_ids)} new stations.")
    station_data = fetch.temperature_now_stations()
    db.insert_station_data(station_data)

    still_unknown_stations = [s for s in station_ids if not db.has_station(s)]
    if still_unknown_stations:
        print(f"Couldn't find data for stations: {still_unknown_stations}")


def update_longterm_measurements(station_ids: list[int]) -> bool:
    if not station_ids:
        return False

    long_update_timestamps = fetch.temperature_published_timestamps("recent")
    for station_id in dump_progress(station_ids, "Updating long-term measurements", unit="stations"):
        published_online = long_update_timestamps.get(station_id)
        data = fetch.temperature_data(station_id, "recent")
        db.insert_temperature_data(station_id, data, published_online)
        db.set_latest_publish_time(station_id, published_online)

    return True


def update_shortterm_measurements(station_ids: dict[int, datetime]):
    if not station_ids:
        return

    for station_id, published_online in dump_progress(list(station_ids.items()), "Updating short-term measurements", unit="stations"):
        data = fetch.temperature_data(station_id, "now")
        db.insert_temperature_data(station_id, data, published_online)
        db.set_latest_publish_time(station_id, published_online)


if __name__ == "__main__":
    run()
