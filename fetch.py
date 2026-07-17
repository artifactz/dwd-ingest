import requests, re, io
from datetime import datetime
import zipfile, csv


URL_TEMP_NOW = "https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/10_minutes/air_temperature/now/"


def temperature_now_timestamps() -> dict[int, datetime]:
    result = {}
    html = requests.get(URL_TEMP_NOW).text
    for match in re.finditer(r'<a href="(10minutenwerte_.+?)">.+?</a>\s+(\d+-\w+-\d+ \d\d:\d\d:\d\d)', html):
        timestamp = datetime.strptime(match[2], "%d-%b-%Y %H:%M:%S")
        id_ = int(match[1].split("_")[2])
        result[id_] = timestamp
    return result


def temperature_now_stations() -> list[dict[str, str]]:
    url = f"{URL_TEMP_NOW}zehn_now_tu_Beschreibung_Stationen.txt"
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


def temperature_now(station_id: int) -> list[dict]:
    url = f"{URL_TEMP_NOW}10minutenwerte_TU_{station_id:05d}_now.zip"
    zip_data = requests.get(url).content
    with zipfile.ZipFile(io.BytesIO(zip_data)) as z:
        namelist = z.namelist()

        assert len(namelist) == 1
        assert namelist[0].endswith(".txt")

        with z.open(namelist[0]) as f:
            csv_data = f.read().decode("utf-8")

    return [row for row in csv.DictReader(csv_data.splitlines(), delimiter=";", skipinitialspace=True)]


if __name__ == "__main__":
    print(temperature_now_timestamps())
