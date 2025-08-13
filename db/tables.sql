DROP TABLE IF EXISTS Location;
DROP TABLE IF EXISTS WeatherVariable;
DROP TABLE IF EXISTS WeatherObservation;

/*
Locations:
Store the geocoding data for the locations found when retrieving my
coordinates.
*/
CREATE TABLE Location(
    num INTEGER,
    lat NUMERIC(3, 6) NOT NULL,
	long NUMERIC(3, 6) NOT NULL,
    name VARCHAR(255) NOT NULL,
    country VARCHAR(255) NOT NULL,

    CONSTRAINT pk_loc PRIMARY KEY (num)
);

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
    cod VARCHAR(12) NOT NULL,
    date DATE NOT NULL,
    time TIME NOT NULL,
    wvariable NUMERIC NOT NULL, /*Weather variable*/
    wvalue INT NOT NULL,/*Weather value*/
    id_location NUMERIC NOT NULL,

    CONSTRAINT pk_wobs PRIMARY KEY (cod),
    CONSTRAINT fk_wvariable FOREIGN KEY (wvariable) REFERENCES WeatherVariable(num),
    CONSTRAINT fk_loc FOREIGN KEY (id_location) REFERENCES Location(num)
)
