# Mortar IO Technical Test

A simple weather API that allows the following:

- GET /weather/(city)
  - Get latest weather report for a given city
 
 ```
Example
{
    "city_name": "LONDON",
    "condition": "cloudy",
    "temperature_celsuis": 12.0,
    "timestamp": "Mon, 30 Oct 2023 12:00:00 GMT"
}

```
- GET /weather 
  - Get latest weather report for all cities (currently only 3, LONDON, MANCHESTER, BRISTOL)

```
Example
{
    "LONDON": {
        "city_name": "LONDON",
        "condition": "cloudy",
        "temperature_celsius": 12.0,
        "timestamp": "Mon, 30 Oct 2023 12:00:00 GMT"
    },
    "MANCHESTER": {
        "city_name": "MANCHESTER",
        "condition": " "rainy",
        "temperature_celsius": 10.0,
        "timestamp": "Mon, 30 Oct 2023 12:00:00 GMT"
    }
    ...
}


```

- POST /weather 
  - Post a new weather report for a given city. Reports are sorted chronologically and only the latest report is returned, historical reports can be added.

 ```
Example
{
    "city_name": "London",
    "condition": "cloudy" | "sunny" | "rainy",
    "temperature_celsuis": 10.0 (float between -50 and 75),
    "timestamp": "2021-01-01T00:00:00Z" (ISO 8601 format)
}

```

- PUT /weather
  - Replace the latest weather report for a given city 

- DELETE /weather/(city) 
  - Delete all weather reports for a given city


## Setup


```bash

docker build . -t mortario-test

# Run tests
docker run --rm mortario-test pytest

# Run flask app on port 5000
docker run -p 5000:5000 mortario-test
```

## Next Steps

- Custom JSON encoder for datetime
  - flask's default dateimte json encoding format is RFC 822 so it serializes to "Mon, 30 Oct 2023 12:00:00 GMT", with more time I would change this to ISO format with a custom json encoder. 

- Add more data exploration
  - Endpoints for listing and possibly CRUD for cities and conditions 
  - Range queries for weather reports within cities
  - More meta data like humidity, wind speed, geolocation etc

- Error handling
  - Write app specific errors like CityNotFound, InvalidCondition etc
  - Formalise error responses with a standard format

