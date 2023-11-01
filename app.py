from datetime import datetime, timezone
import json
from flask import Flask, jsonify, request
from pydantic import ValidationError

from models import (
    WEATHER_REPORTS,
    WeatherCityQuery,
    WeatherReport,
    add_report,
    city_exists,
    delete_all_weather_reports,
    get_latest_report,
    get_latest_report_all_cities,
    set_latest_report,
)

app = Flask(__name__)


@app.post("/weather")
def weather_report_create():
    # could make this endpoint /weather/<city> but, as the city
    # is contained in the post body, just using /weather to avoid redundancy.
    # Depends on API design decision

    try:
        report = WeatherReport(**request.json)
    except ValidationError as ex:
        # shortcut to get pydantic validation errors as json
        # flask json can't handle pydantic errors so we need to
        # use pydantic's json encoder with ex.json() then load it
        # back into a dict to hand back to flask's json encoding

        return {
            "message": "Invalid weather report",
            "errors": json.loads(ex.json()),
        }, 400

    # valid weather report, add to data store

    added_report = add_report(report)

    return jsonify(added_report), 201


@app.put("/weather")
def weather_report_update():
    # update the latest weather report for a city
    try:
        report = WeatherReport(**request.json)
    except ValidationError as ex:
        return {
            "message": "Invalid weather report",
            "errors": json.loads(ex.json()),
        }, 400

    # valid weather report, add to data store

    updated_report = set_latest_report(report)

    return jsonify(updated_report), 201


@app.delete("/weather/<city>")
def weather_report_delete_all(city):
    try:
        query = WeatherCityQuery(city_name=city)
    except ValidationError as ex:
        return json.loads(ex.json()), 400

    city_name = query.city_name

    if not city_exists(city_name):
        return jsonify({"message": f"City not found: {city}"}), 404

    delete_all_weather_reports(city_name)

    return jsonify({"message": f"Deleted all reports for {city}"})


@app.get("/weather/<city>")
def weather_report_latest(city):
    try:
        query = WeatherCityQuery(city_name=city)
    except ValidationError as ex:
        return json.loads(ex.json())

    city_name = query.city_name

    if not city_exists(city_name):
        return jsonify({"message": f"City not found: {city}"}), 404

    report = get_latest_report(city_name)

    if report is None:
        return jsonify({"message": f"No reports for city: {city}"}), 404

    return jsonify(report)


@app.get("/weather")
def weather_report_latest_all_cities():
    return jsonify(get_latest_report_all_cities())


if __name__ == "__main__":
    # add some test data for development
    for city, reports in WEATHER_REPORTS.items():
        reports.append(
            {
                "city_name": city,
                "temperature_celsius": 15,
                "timestamp": datetime.now(tz=timezone.utc),
                "condition": "sunny",
            }
        )

    # 0.0.0.0 needed for docker
    app.run(host="0.0.0.0")
