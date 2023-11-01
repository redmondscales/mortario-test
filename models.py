from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, field_validator, AwareDatetime

available_cities = ["LONDON", "BRISTOL", "MANCHESTER"]

WEATHER_REPORTS = {city: [] for city in available_cities}


class WeatherCityQuery(BaseModel):
    # GET request validator for get weather report
    city_name: str

    @field_validator("city_name")
    def city_upper(cls, v):
        return v.upper()


class WeatherReport(BaseModel):
    # pydantic model for a weather report
    # convert to uppercase

    class Condition(str, Enum):
        SUNNY = "sunny"
        CLOUDY = "cloudy"
        RAINY = "rainy"

    city_name: str
    temperature_celsius: float
    condition: Condition
    timestamp: AwareDatetime

    @field_validator("temperature_celsius")
    def realistic_temperature(cls, v):
        # world record temp is 56.7C to -89.2C
        if v > 75 or v < -100:
            raise ValueError("Temperature must be between -100 and 75.")

        return v

    @field_validator("timestamp")
    def not_future_timestamp(cls, v):
        # simple check, doesn't account for timezones
        if v > datetime.now(tz=timezone.utc):
            raise ValueError("Timestamp cant be in future.")

        return v

    @field_validator("city_name")
    def city_must_exist(cls, v):
        city_upper = v.upper()
        if not city_exists(city_upper):
            raise ValueError("City not found.")
        return city_upper


def city_exists(city):
    return city in WEATHER_REPORTS


def sort_weather_reports(city):
    # sort weather reports for a city by timestamp
    WEATHER_REPORTS[city].sort(key=lambda x: x["timestamp"])

    return WEATHER_REPORTS[city]


def get_latest_report_all_cities():
    return {
        city: get_latest_report(city)
        for city in WEATHER_REPORTS
        # if WEATHER_REPORTS[city]
    }


def get_latest_report(city):
    try:
        return WEATHER_REPORTS[city][-1]
    except IndexError:
        return None


def add_report(new_report: WeatherReport):
    new_report_dict = new_report.model_dump()

    # get latest existing to compare to new report, if new
    # report is before latest, weather reports need resorting

    latest_report = get_latest_report(new_report.city_name)

    reports = WEATHER_REPORTS[new_report.city_name]
    reports.append(new_report_dict)

    if latest_report and new_report.timestamp < latest_report["timestamp"]:
        # new report is before the current latest report
        sort_weather_reports(new_report.city_name)

    return new_report_dict


def set_latest_report(report: WeatherReport):
    report_dict = report.model_dump()

    if WEATHER_REPORTS[report.city_name]:
        WEATHER_REPORTS[report.city_name][-1] = report_dict
    else:
        WEATHER_REPORTS[report.city_name].append(report_dict)

    return report_dict


def delete_all_weather_reports(city):
    WEATHER_REPORTS[city] = []

    return WEATHER_REPORTS[city]
