DROP TABLE IF EXISTS Accommodation CASCADE;
DROP TABLE IF EXISTS Country CASCADE;
DROP TABLE IF EXISTS Location CASCADE;
DROP TABLE IF EXISTS Place CASCADE;
DROP TABLE IF EXISTS Athlete CASCADE;
DROP TABLE IF EXISTS Member CASCADE;
DROP TABLE IF EXISTS Staff CASCADE;
DROP TABLE IF EXISTS Official CASCADE;
DROP TABLE IF EXISTS Participates CASCADE;
DROP TABLE IF EXISTS Team CASCADE;
DROP TABLE IF EXISTS Booking CASCADE;
DROP TABLE IF EXISTS Event CASCADE;
DROP TABLE IF EXISTS IndividualEvent CASCADE;
DROP TABLE IF EXISTS Journey CASCADE;
DROP TABLE IF EXISTS RunsEvent CASCADE;
DROP TABLE IF EXISTS Sport CASCADE;
DROP TABLE IF EXISTS SportVenue CASCADE;
DROP TABLE IF EXISTS TeamEvent CASCADE;
DROP TABLE IF EXISTS TeamMember CASCADE;
DROP TABLE IF EXISTS Vehicle CASCADE;

CREATE TABLE Country(
    country_code CHAR(3) PRIMARY KEY,
    iso_code CHAR(2) UNIQUE,
    country_name VARCHAR(40)
);

--
-- Place location hierarchy
--
CREATE TABLE Location (
   location_id	INT PRIMARY KEY, -- surrogate key
   name      VARCHAR(80) NOT NULL,
   loc_type      VARCHAR(10) NOT NULL,
   part_of    INTEGER REFERENCES Location, -- NOTE: can be NULL
   CONSTRAINT location_KEY UNIQUE(name, part_of), -- natural key
   CONSTRAINT location_CHK CHECK (loc_type IN ('eventvenue','suburb','area','region','city','state','country'))
);

CREATE TABLE Place (
    place_id INT PRIMARY KEY, -- surrogate key
    place_name 	VARCHAR(80) UNIQUE, -- natural key
    gps_long	REAL,
    gps_lat	REAL,
    address	VARCHAR(200),
    located_in	INT REFERENCES Location
);

CREATE TABLE SportVenue (
    place_id INT PRIMARY KEY REFERENCES Place
);

CREATE TABLE Accommodation (
    place_id INT PRIMARY KEY REFERENCES Place
);

--
-- Member hierarchy
--
CREATE TABLE Member (
    member_id	char(10) PRIMARY KEY,
    title	VARCHAR(4) CHECK(title IN ('Mr', 'Mrs', 'Ms', 'Miss', 'Dr')),
    family_name		VARCHAR(30),
    given_names		VARCHAR(30),
    country_code	CHAR(3) REFERENCES Country NOT NULL,
    accommodation	INT REFERENCES Accommodation,
    pass_word VARCHAR(20)
);

CREATE TABLE Athlete (
    member_id	char(10) PRIMARY KEY REFERENCES Member
);

CREATE TABLE Official (
    member_id	char(10) PRIMARY KEY REFERENCES Member
);

CREATE TABLE Staff (
  member_id	char(10) PRIMARY KEY REFERENCES Member
);

-- Sports
CREATE TABLE Sport (
	sport_id INT PRIMARY KEY, -- surrogate key
	sportcode CHAR(2) NOT NULL,
	sport_name VARCHAR(20) NOT NULL,
	discipline VARCHAR(20),
	UNIQUE (sport_name, discipline) -- natural key
);

-- Events
CREATE TABLE Event (
    event_id INT PRIMARY KEY,  -- surrogate key
    sport_id INT REFERENCES Sport,
    event_name      VARCHAR(50),
    event_gender CHAR,
    UNIQUE(sport_id, event_name, event_gender), -- natural key
    sport_venue     INT REFERENCES SportVenue,
    event_start      TIMESTAMP,
    result_type     VARCHAR -- Not supported in A3 client
);

CREATE TABLE RunsEvent (
    event_id   INT REFERENCES Event,
    member_id CHAR(10) REFERENCES Official,
    role VARCHAR(10),
    PRIMARY KEY (event_id, member_id)
);

CREATE TABLE TeamEvent (
    event_id   INT PRIMARY KEY REFERENCES Event
);

CREATE TABLE IndividualEvent (
    event_id   INT PRIMARY KEY REFERENCES Event
);

CREATE TABLE Team (
    event_id   INT REFERENCES TeamEvent,
    team_name  VARCHAR(20),
    country_code	CHAR(3) REFERENCES Country,
    medal CHAR CHECK (medal IN ('G','S','B')), -- Could add a UNIQUE(event,medal)
    PRIMARY KEY (event_id, team_name)
);

CREATE TABLE TeamMember (
    event_id   INT,
    team_name  VARCHAR(20),
    FOREIGN KEY (event_id, team_name) REFERENCES Team,
    athlete_id CHAR(10) REFERENCES Athlete,
    PRIMARY KEY (event_id, team_name, athlete_id)
    -- actually (team_name, athlete_id) and (event_id, athlete_id) are keys
);

CREATE TABLE Participates (
    event_id   INT REFERENCES IndividualEvent,
    athlete_id CHAR(10) REFERENCES Athlete,
    medal CHAR CHECK (medal IN ('G','S','B')), -- Could add a UNIQUE(event,medal)
    PRIMARY KEY (event_id, athlete_id)
);

CREATE TABLE Vehicle (
    vehicle_code	CHAR(8) PRIMARY KEY,
    capacity	    INTEGER NOT NULL
);

CREATE TABLE Journey (
	journey_id INT PRIMARY KEY, -- surrogate key
    depart_time	    TIMESTAMP,
    from_place	    INT NOT NULL REFERENCES Place,
    to_place	    INT NOT NULL REFERENCES Place,
    vehicle_code	CHAR(8) NOT NULL REFERENCES Vehicle,
    nbooked		    INTEGER NOT NULL DEFAULT 0,
    UNIQUE (vehicle_code, depart_time) -- natural key
);

CREATE TABLE Booking (
    booked_for	CHAR(10) REFERENCES Member,
    booked_by	CHAR(10) NOT NULL REFERENCES Staff,
    when_booked	    TIMESTAMP,
    journey_id INT REFERENCES Journey,
    PRIMARY KEY(journey_id, booked_for) -- natural key
);

CREATE OR REPLACE FUNCTION update_journey_nbooked() RETURNS TRIGGER AS $journey_nbooked$ BEGIN IF(TG_OP = 'DELETE') THEN UPDATE Journey SET nbooked = nbooked - 1 WHERE journey_id = OLD.journey_id; RETURN OLD; ELSIF(TG_OP = 'INSERT') THEN UPDATE Journey SET nbooked = nbooked + 1 WHERE journey_id = NEW.journey_id; RETURN NEW; END IF; RETURN NULL; END; $journey_nbooked$ LANGUAGE plpgsql;
CREATE TRIGGER trg_update_journey_nbooked AFTER INSERT OR DELETE ON Booking FOR EACH ROW EXECUTE PROCEDURE update_journey_nbooked();
