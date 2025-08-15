DROP TABLE IF EXISTS WeatherVariable;
DROP TABLE IF EXISTS WeatherObservation;

/*
Weather Observations:
Store the temperature, wind and precipitation forecasts for a specific
location.
*/

CREATE TABLE WeatherVariable(
    num INTEGER,
    name VARCHAR(13),
    unit VARCHAR(255) NOT NULL,

    CONSTRAINT pk_wvar PRIMARY KEY (num)
);

INSERT INTO WeatherVariable(name, unit) VALUES
    ('temperature', 'degC'),
    ('wind', 'kmh_deg'),
    ('precipitation', 'lm2');


CREATE TABLE WeatherObservation(
    cod INTEGER,
    date DATE NOT NULL,
    time TIME NOT NULL,
    wvariable NUMERIC NOT NULL, /*Weather variable*/
    wvalue INT NOT NULL,/*Weather value*/

    CONSTRAINT pk_wobs PRIMARY KEY (cod),
    CONSTRAINT fk_wvariable FOREIGN KEY (wvariable) REFERENCES WeatherVariable(num)
)
