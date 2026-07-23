import time, functools
from datetime import datetime, date, timedelta
import fetch, db
from dump_progress import dump_progress


def run(interval_seconds=60):
    while True:

        # There are two data sources:
        #
        # - "Now" data starts at 00:00 UTC of the current day and is published every half hour at 20 and 50
        #   minutes (short-term update).
        # - "Recent" data ends at 23:50 UTC of the previous day, goes back several months, is published around
        #   01:30 UTC and takes a long time to download (long-term update).
        #
        # We only do long-term updates if there is a gap in the data since the last fetch and we only do them once
        # per day (there are rare cases where the recent data ends earlier, not closing the gap).

        unknown_stations, short_update_stations, long_update_stations = determine_stations()

        update_stations(unknown_stations)

        if update_measurements(long_update_stations, "recent"):
            # This takes ~1h, so previous data from determine_stations() is outdated at this point
            continue

        update_measurements(short_update_stations, "now")

        if not unknown_stations and not short_update_stations and not long_update_stations:
            print("No updates.")

        time.sleep(interval_seconds)


def determine_stations() -> tuple[list[int], dict[int, datetime], dict[int, datetime]]:
    """
    Retrieves stations from the temperature/now index page and puts them into one or two of three bins, respectively,
    according to these rules in the following priority:

    - A new station is not in the database yet:
      unknown, long_update
    - A station is missing yesterday's 23:50 update and there is new temperature/recent data to download:
      long_update
    - There is new temperature/now data:
      short_update

    Returns:
        - unknown_stations: list of IDs
        - short_update_stations: dict of IDs to published timestamps
        - long_update_stations: dict of IDs to published timestamps
    """
    timestamps_now = fetch.temperature_published_timestamps("now")

    @functools.cache
    def get_timestamps_recent():
        """Lazy cached fetch"""
        return fetch.temperature_published_timestamps("recent")

    unknown_stations = []
    short_update_stations = {}
    long_update_stations = {}

    for station_id, now_published_online_ts in timestamps_now.items():

        if not db.has_station(station_id):
            unknown_stations.append(station_id)

        now_published_db_ts = db.get_latest_publish_time(station_id, "now")
        recent_published_db_ts = db.get_latest_publish_time(station_id, "recent")
        yesterday = date.today() - timedelta(days=1)
        latest_ts_yesterday_db = db.get_latest_temperature_timestamp_on_day(station_id, yesterday)

        # First time seeing this station:
        if recent_published_db_ts is None:
            long_update_stations[station_id] = get_timestamps_recent().get(station_id)

        # Yesterday's last update is missing and there's new long-term data:
        elif (
            (latest_ts_yesterday_db is None or latest_ts_yesterday_db.hour < 23 or latest_ts_yesterday_db.minute < 40) and
            station_id in get_timestamps_recent() and get_timestamps_recent()[station_id] > recent_published_db_ts
        ):
            long_update_stations[station_id] = get_timestamps_recent()[station_id]

        # There's new short-term data
        elif now_published_db_ts is None or now_published_online_ts > now_published_db_ts:
            short_update_stations[station_id] = now_published_online_ts

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


def update_measurements(station_publish_timestamps: dict[int, datetime], term: str) -> bool:
    term = term.lower()
    assert term == "now" or term == "recent"

    if not station_publish_timestamps:
        return False

    desc_term_str = "short-term" if term == "now" else "long-term"
    for station_id, published_online in dump_progress(
        list(station_publish_timestamps.items()),
        desc=f"Updating {desc_term_str} measurements",
        unit="stations"
    ):
        data = fetch.temperature_data(station_id, term)
        db.insert_temperature_data(station_id, data, published_online)
        db.set_latest_publish_time(station_id, term, published_online)

    return True


if __name__ == "__main__":
    run()
