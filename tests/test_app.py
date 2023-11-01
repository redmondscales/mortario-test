from datetime import datetime, timedelta, timezone
import pytest
from app import WeatherReport, app
from models import WEATHER_REPORTS


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_404_if_no_reports(client):
    response = client.get("/weather/london")
    assert response.status_code == 404


def test_can_post_report(client):
    report = {
        "city_name": "London",
        "temperature_celsius": 10,
        "timestamp": "2023-10-30T12:00:00Z",
        "condition": WeatherReport.Condition.SUNNY,
    }
    response = client.post("/weather", json=report)

    assert response.status_code == 201
    created = response.get_json()

    assert created["city_name"] == report["city_name"].upper()
    assert created["temperature_celsius"] == report["temperature_celsius"]

    # flask default dateimte json encoding format is RFC 822 for some reason
    # with more time I would change this to ISO format with a custom json encoder.
    # hardcoding the timestamp in RFC 822 here just for this test
    assert created["timestamp"] == "Mon, 30 Oct 2023 12:00:00 GMT"
    assert created["condition"] == report["condition"]


def test_cant_report_if_city_not_allowed(client):
    report = {
        "city_name": "Paris",
        "temperature_celsius": 10,
        "timestamp": "2023-10-30T12:00:00Z",
        "condition": WeatherReport.Condition.SUNNY,
    }
    response = client.post("/weather", json=report)

    assert response.status_code == 400
    assert response.get_json()["errors"][0]["msg"] == "Value error, City not found."


def test_cant_report_unrealistic_temperature(client):
    report = {
        "city_name": "London",
        "temperature_celsius": 100,
        "timestamp": "2023-10-30T12:00:00Z",
        "condition": WeatherReport.Condition.SUNNY,
    }
    response = client.post("/weather", json=report)

    assert response.status_code == 400
    assert (
        response.get_json()["errors"][0]["msg"]
        == "Value error, Temperature must be between -100 and 75."
    )

    report = {
        "city_name": "London",
        "temperature_celsius": -101,
        "timestamp": "2023-10-30T12:00:00Z",
        "condition": WeatherReport.Condition.SUNNY,
    }
    response = client.post("/weather", json=report)

    assert response.status_code == 400
    assert (
        response.get_json()["errors"][0]["msg"]
        == "Value error, Temperature must be between -100 and 75."
    )


def test_cant_report_in_future(client):
    later = datetime.now(tz=timezone.utc) + timedelta(hours=1)
    report = {
        "city_name": "London",
        "temperature_celsius": 10,
        "timestamp": later.isoformat(),
        "condition": WeatherReport.Condition.SUNNY,
    }
    response = client.post("/weather", json=report)

    assert response.status_code == 400
    assert (
        response.get_json()["errors"][0]["msg"]
        == "Value error, Timestamp cant be in future."
    )


def test_cant_report_invalid_condition(client):
    report = {
        "city_name": "London",
        "temperature_celsius": 10,
        "timestamp": "2023-10-30T12:00:00Z",
        "condition": "wrong",
    }
    response = client.post("/weather", json=report)

    assert response.status_code == 400
    assert (
        response.get_json()["errors"][0]["msg"]
        == "Input should be 'sunny', 'cloudy' or 'rainy'"
    )


def test_can_get_latest_report(client):
    # create two reports, second one is before the first one
    # check the first one is returned on GET

    latest_report = {
        "city_name": "London",
        "temperature_celsius": 15,
        "timestamp": "2023-10-30T13:00:00Z",
        "condition": WeatherReport.Condition.SUNNY,
    }

    earlier_report = {
        "city_name": "London",
        "temperature_celsius": 10,
        "timestamp": "2023-10-30T12:00:00Z",
        "condition": WeatherReport.Condition.SUNNY,
    }

    client.post("/weather", json=latest_report)
    client.post("/weather", json=earlier_report)

    response = client.get("/weather/london")
    assert response.status_code == 200
    response_json = response.get_json()
    assert response_json["temperature_celsius"] == latest_report["temperature_celsius"]


def test_can_delete_reports(client):
    report = {
        "city_name": "London",
        "temperature_celsius": 10,
        "timestamp": "2023-10-30T12:00:00Z",
        "condition": WeatherReport.Condition.SUNNY,
    }
    client.post("/weather/london", json=report)

    response = client.delete("/weather/london")
    assert response.status_code == 200

    response = client.get("/weather/london")
    assert response.status_code == 404


def test_404_delete_city_not_found(client):
    response = client.delete("/weather/wrong")
    assert response.status_code == 404


def test_can_set_latest_report(client):
    # check put request replaces latest report
    WEATHER_REPORTS["LONDON"] = [
        {
            "city_name": "London",
            "temperature_celsius": 15,
            "timestamp": "2023-10-30T13:00:00Z",
            "condition": WeatherReport.Condition.SUNNY,
        }
    ]

    new_report = {
        "city_name": "London",
        "temperature_celsius": 10,
        "timestamp": "2023-10-30T12:00:00Z",
        "condition": WeatherReport.Condition.SUNNY,
    }
    response = client.put("/weather", json=new_report)

    assert response.status_code == 201

    response = client.get("/weather/london")
    assert response.status_code == 200
    latest = response.get_json()
    assert latest["temperature_celsius"] == new_report["temperature_celsius"]
    assert len(WEATHER_REPORTS["LONDON"]) == 1


def test_can_get_latest_all_cities(client):
    WEATHER_REPORTS["LONDON"] = [
        {
            "city_name": "LONDON",
            "temperature_celsius": 15,
            "timestamp": "2023-10-30T13:00:00Z",
            "condition": WeatherReport.Condition.SUNNY,
        }
    ]

    WEATHER_REPORTS["MANCHESTER"] = [
        {
            "city_name": "MANCHESTER",
            "temperature_celsius": 18,
            "timestamp": "2023-10-30T12:00:00Z",
            "condition": WeatherReport.Condition.CLOUDY,
        },
        {
            "city_name": "MANCHESTER",
            "temperature_celsius": 20,
            "timestamp": "2023-10-30T13:00:00Z",
            "condition": WeatherReport.Condition.SUNNY,
        },
    ]

    response = client.get("/weather")
    assert response.status_code == 200
    latest = response.get_json()
    assert len(latest) == 3
    assert latest["LONDON"]["temperature_celsius"] == 15
    assert latest["MANCHESTER"]["temperature_celsius"] == 20
    assert latest["BRISTOL"] is None
