from typing import Optional
import os, time
from datetime import datetime
import psycopg2


PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = int(os.getenv("PG_PORT", "5432"))
PG_DB = os.getenv("PG_DB", "dwd")
PG_USER = os.getenv("PG_USER", "dwd_writer")
PG_PASS = os.getenv("PG_PASS", "dwdw")


def _connect(total_timeout_seconds: float = 20.0, initial_wait_seconds: float = 0.25, wait_scale: float = 1.5):
    """
    Connects with retries.

    Args:
        total_timeout_seconds: Total time to wait for the database to become available.
        initial_wait_seconds: Initial wait time before retrying.
        wait_scale: Scale factor for increasing wait time after each retry.

    Returns:
        psycopg2 connection object.
    """
    t0 = time.time()
    wait_seconds = initial_wait_seconds

    while time.time() - t0 < total_timeout_seconds:
        try:
            return psycopg2.connect(database=PG_DB, user=PG_USER, password=PG_PASS, host=PG_HOST, port=PG_PORT)

        except psycopg2.OperationalError:
            print("Waiting for database...")
            time.sleep(wait_seconds)
            wait_seconds *= wait_scale

    raise RuntimeError(f"Could not connect to database after {total_timeout_seconds} seconds.")


connection = _connect()


def has_station(station_id: int) -> bool:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1 FROM station WHERE id = %s", (station_id,))
        return cursor.fetchone() is not None


def insert_station_data(data: list[dict[str, str]]):
    now = datetime.now()
    params = []
    for row in data:
        id_ = int(row["Stations_id"])
        date_from = datetime.strptime(row["von_datum"], "%Y%m%d")
        date_to = datetime.strptime(row["bis_datum"], "%Y%m%d")
        altitude = int(row["Stationshoehe"])
        lat = float(row["geoBreite"])
        lon = float(row["geoLaenge"])
        name = row["Stationsname"]
        region = row["Bundesland"]
        params.append((id_, date_from, date_to, altitude, lat, lon, name, region, now))

    sql = f"""INSERT INTO station (id, date_from, date_to, altitude_m, latitude_deg, longitude_deg,
                                   name, region, timestamp_added)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    date_from = EXCLUDED.date_from,
                    date_to = EXCLUDED.date_to,
                    altitude_m = EXCLUDED.altitude_m,
                    latitude_deg = EXCLUDED.latitude_deg,
                    longitude_deg = EXCLUDED.longitude_deg,
                    name = EXCLUDED.name,
                    region = EXCLUDED.region,
                    timestamp_added = EXCLUDED.timestamp_added"""

    with connection.cursor() as cursor:
        cursor.executemany(sql, params)
    connection.commit()


def get_latest_publish_time(station_id: int) -> Optional[datetime]:
    with connection.cursor() as cursor:
        cursor.execute("SELECT temperature_published_timestamp FROM station WHERE id = %s", (station_id,))
        result = cursor.fetchone()
        return result[0] if result else None


def set_latest_publish_time(station_id: int, timestamp: datetime):
    with connection.cursor() as cursor:
        cursor.execute("UPDATE station SET temperature_published_timestamp = %s WHERE id = %s", (timestamp, station_id))
    connection.commit()


def insert_temperature_data(station_id: int, data: list[dict], published_online: datetime):
    now = datetime.now()
    params = []
    for row in data:
        timestamp = datetime.strptime(row["MESS_DATUM"], "%Y%m%d%H%M")
        quality = int(row["QN"])
        pressure = float(row["PP_10"])
        temperature_2m = float(row["TT_10"])
        temperature_5cm = float(row["TM5_10"])
        humidity = float(row["RF_10"])
        dew = float(row["TD_10"])
        params.append((station_id, timestamp, quality, pressure, temperature_2m, temperature_5cm, humidity, dew, published_online, now))

    sql = f"""INSERT INTO temperature (station_id, timestamp, quality, pressure_hpa, temperature_2m_c,
                                       temperature_5cm_c, humidity_percent, dew_point_temperature_c, timestamp_published, timestamp_added)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (station_id, timestamp) DO UPDATE SET
                    quality = EXCLUDED.quality,
                    pressure_hpa = EXCLUDED.pressure_hpa,
                    temperature_2m_c = EXCLUDED.temperature_2m_c,
                    temperature_5cm_c = EXCLUDED.temperature_5cm_c,
                    humidity_percent = EXCLUDED.humidity_percent,
                    dew_point_temperature_c = EXCLUDED.dew_point_temperature_c,
                    timestamp_published = EXCLUDED.timestamp_published,
                    timestamp_added = EXCLUDED.timestamp_added"""

    with connection.cursor() as cursor:
        cursor.executemany(sql, params)
    connection.commit()
