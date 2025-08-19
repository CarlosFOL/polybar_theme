DROP TABLE IF EXISTS WeatherObservation;

/*
Weather Observations:
Store the temperature, wind and precipitation forecasts for a specific
location.
*/
CREATE TABLE WeatherObservation(
    num INTEGER,
    date DATE NOT NULL,
    time TIME NOT NULL,
    temperature NUMERIC NOT NULL,
    wind NUMERIC NOT NULL,
    precipitation NUMERIC NOT NULL,

    CONSTRAINT pk_wobs PRIMARY KEY (num)
)
