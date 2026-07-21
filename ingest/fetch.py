import requests, re, io
from datetime import datetime
import zipfile, csv


TEMPERATURE_URL = "https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/10_minutes/air_temperature/"


def temperature_published_timestamps(term: str) -> dict[int, datetime]:
    result = {}
    html = requests.get(get_index_url(term)).text
    for match in re.finditer(r'<a href="(10minutenwerte_.+?)">.+?</a>\s+(\d+-\w+-\d+ \d\d:\d\d:\d\d)', html):
        timestamp = datetime.strptime(match[2], "%d-%b-%Y %H:%M:%S")
        id_ = int(match[1].split("_")[2])
        result[id_] = timestamp
    return result


def temperature_now_stations() -> list[dict[str, str]]:
    url = f"{TEMPERATURE_URL}/now/zehn_now_tu_Beschreibung_Stationen.txt"
    txt_data = requests.get(url).text
    lines = txt_data.splitlines()
    headers = lines[0].split()

    assert headers == ["Stations_id", "von_datum", "bis_datum", "Stationshoehe", "geoBreite", "geoLaenge", "Stationsname", "Bundesland", "Abgabe"]

    result = []
    for line in lines[2:]:
        match = re.match(r"(.+?)\s+(.+?)\s+(.+?)\s\s+(.+?)\s\s+(.+?)\s\s+(.+?)\s+(.+?)\s\s+(.+?)\s\s+(.+?)\s*", line)
        if match is None:
            raise
        item = {}
        for i, header in enumerate(headers):
            item[header] = match[i + 1]
        result.append(item)

    return result


def temperature_data(station_id: int, term: str) -> list[dict]:
    url = get_data_url(station_id, term)
    zip_data = requests.get(url).content
    with zipfile.ZipFile(io.BytesIO(zip_data)) as z:
        namelist = z.namelist()

        assert len(namelist) == 1
        assert namelist[0].endswith(".txt")

        with z.open(namelist[0]) as f:
            csv_data = f.read().decode("utf-8")

    return [row for row in csv.DictReader(csv_data.splitlines(), delimiter=";", skipinitialspace=True)]


def get_index_url(term: str) -> str:
    term = term.lower()
    assert term == "now" or term == "recent"
    return f"{TEMPERATURE_URL}/{term}/"


def get_data_url(station_id: int, term: str) -> str:
    term = term.lower()
    assert term == "now" or term == "recent"
    suffix = "now" if term == "now" else "akt"
    return f"{TEMPERATURE_URL}/{term}/10minutenwerte_TU_{station_id:05d}_{suffix}.zip"
