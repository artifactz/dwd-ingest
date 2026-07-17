import time
import fetch, db
from tqdm import tqdm


def run(interval_seconds=60):
    while True:
        timestamps = fetch.temperature_now_timestamps()
        unknown_stations = []
        updated_stations = {}

        for station_id, published_online in timestamps.items():

            if not db.has_station(station_id):
                unknown_stations.append(station_id)

            published_db = db.get_latest_publish_time(station_id)
            if published_db is None or published_online > published_db:
                updated_stations[station_id] = published_online

        if unknown_stations:
            print(f"Discovered {len(unknown_stations)} new stations.")
            station_data = fetch.temperature_now_stations()
            db.insert_station_data(station_data)

            still_unknown_stations = [s for s in unknown_stations if not db.has_station(s)]
            if still_unknown_stations:
                print(f"Couldn't find data for stations: {still_unknown_stations}")

        if updated_stations:
            for station_id, published_online in tqdm(updated_stations.items(), "Updating measurements", unit="stations"):
                data = fetch.temperature_now(station_id)
                db.insert_temperature_data(station_id, data, published_online)
                db.set_latest_publish_time(station_id, published_online)
            print("Done.")

        if not unknown_stations and not updated_stations:
            print("No updates.")

        time.sleep(interval_seconds)


if __name__ == "__main__":
    run()
