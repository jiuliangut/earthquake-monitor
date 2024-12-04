DROP TABLE IF EXISTS earthquakes;
DROP TABLE IF EXISTS user_topic_assignment;
DROP TABLE IF EXISTS topics;
DROP TABLE IF EXISTS alerts;
DROP TABLE IF EXISTS magnitude;
DROP TABLE IF EXISTS networks;
DROP TABLE IF EXISTS type;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS regions;

CREATE TABLE alerts (
    alert_id SMALLINT GENERATED ALWAYS AS IDENTITY,
    alert_type VARCHAR(6) UNIQUE NOT NULL,
    PRIMARY KEY (alert_id)
);

CREATE TABLE magnitude (
    magnitude_id SMALLINT GENERATED ALWAYS AS IDENTITY,
    magnitude_type VARCHAR(3) UNIQUE NOT NULL,
    PRIMARY KEY (magnitude_id)
);

CREATE TABLE networks (
    network_id SMALLINT GENERATED ALWAYS AS IDENTITY,
    network_name VARCHAR(2) UNIQUE NOT NULL,
    PRIMARY KEY (network_id)
);

CREATE TABLE type (
    type_id SMALLINT GENERATED ALWAYS AS IDENTITY,
    type_name VARCHAR(10) UNIQUE NOT NULL,
    PRIMARY KEY (type_id)
);

CREATE TABLE earthquakes (
    earthquake_id BIGINT GENERATED ALWAYS AS IDENTITY,
    time TIMESTAMPTZ NOT NULL,
    tsunami BOOLEAN NOT NULL,
    felt_report_count SMALLINT NOT NULL,
    magnitude DECIMAL NOT NULL,
    cdi DECIMAL NOT NULL,
    latitude DECIMAL NOT NULL,
    longitude DECIMAL NOT NULL,
    detail_url VARCHAR(255) UNIQUE NOT NULL,
    alert_id SMALLINT,
    magnitude_id SMALLINT,
    network_id SMALLINT,
    type_id SMALLINT,
    PRIMARY KEY (earthquake_id),
    FOREIGN KEY (alert_id) REFERENCES alerts(alert_id),
    FOREIGN KEY (magnitude_id) REFERENCES magnitude(magnitude_id),
    FOREIGN KEY (network_id) REFERENCES networks(network_id),
    FOREIGN KEY (type_id) REFERENCES type(type_id),
    CONSTRAINT latitude_range CHECK (latitude BETWEEN -90.0 AND 90.0),
    CONSTRAINT longitude_range CHECK (longitude BETWEEN -180.0 AND 180.0)
);

CREATE TABLE users (
    user_id BIGINT GENERATED ALWAYS AS IDENTITY,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(15) UNIQUE NOT NULL,
    PRIMARY KEY (user_id)
);

CREATE TABLE regions (
    region_id SMALLINT GENERATED ALWAYS AS IDENTITY,
    min_latitude DECIMAL NOT NULL,
    max_latitude DECIMAL NOT NULL,
    min_longitude DECIMAL NOT NULL,
    max_longitude DECIMAL NOT NULL,
    region_name VARCHAR(100) UNIQUE NOT NULL,
    PRIMARY KEY (region_id)
);

CREATE TABLE topics (
    topic_id SMALLINT GENERATED ALWAYS AS IDENTITY,
    min_magnitude_value SMALLINT NOT NULL,
    region_id SMALLINT,
    PRIMARY KEY (topic_id),
    FOREIGN KEY (region_id) REFERENCES regions(region_id)
);

CREATE TABLE user_topic_assignment (
    assignment_id BIGINT GENERATED ALWAYS AS IDENTITY,
    user_id BIGINT,
    topic_id SMALLINT,
    PRIMARY KEY (assignment_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (topic_id) REFERENCES topics(topic_id)
);

INSERT INTO alerts (alert_type) VALUES 
    ('green'), 
    ('yellow'), 
    ('orange'), 
    ('red');

INSERT INTO magnitude (magnitude_type) VALUES 
    ('md'), 
    ('ml'), 
    ('ms'), 
    ('mw'), 
    ('me'), 
    ('mi'), 
    ('mb'), 
    ('mlg');

INSERT INTO networks (network_name) VALUES 
    ('ak'), 
    ('at'), 
    ('ci'), 
    ('hv'), 
    ('ld'), 
    ('mb'), 
    ('nc'), 
    ('nm'), 
    ('nn'), 
    ('pr'), 
    ('pt'), 
    ('se'), 
    ('tx'),
    ('us'), 
    ('uu'), 
    ('uw');

INSERT INTO type (type_name) VALUES 
    ('earthquake'), 
    ('quarry');

INSERT INTO regions (min_latitude, max_latitude, min_longitude, max_longitude, region_name) VALUES
(-90.0, -60.0, -180.0, -120.0, 'South Pacific Ocean'),
(-90.0, -60.0, -120.0, -60.0, 'South America (Southern Cone)'),
(-90.0, -60.0, -60.0, 0.0, 'Southern Brazil'),
(-90.0, -60.0, 0.0, 60.0, 'South Atlantic Ocean'),
(-90.0, -60.0, 60.0, 120.0, 'Southern Africa (Southern Ocean)'),
(-90.0, -60.0, 120.0, 180.0, 'South Indian Ocean'),
(-60.0, -30.0, -180.0, -120.0, 'Pacific Ocean (Chile & Peru)'),
(-60.0, -30.0, -120.0, -60.0, 'Argentina & Uruguay'),
(-60.0, -30.0, -60.0, 0.0, 'Southeast Brazil'),
(-60.0, -30.0, 0.0, 60.0, 'West Africa (Gulf of Guinea)'),
(-60.0, -30.0, 60.0, 120.0, 'Southern Madagascar & Mozambique'),
(-60.0, -30.0, 120.0, 180.0, 'Indian Ocean (Mascarene Islands)'),
(-30.0, 0.0, -180.0, -120.0, 'Equatorial Pacific Ocean'),
(-30.0, 0.0, -120.0, -60.0, 'Coastal Ecuador & Colombia'),
(-30.0, 0.0, -60.0, 0.0, 'Northern South America'),
(-30.0, 0.0, 0.0, 60.0, 'Central Africa (Congo Basin)'),
(-30.0, 0.0, 60.0, 120.0, 'East Africa (Kenya & Tanzania)'),
(-30.0, 0.0, 120.0, 180.0, 'Indian Ocean (Comoros Islands)'),
(0.0, 30.0, -180.0, -120.0, 'Eastern Pacific Ocean'),
(0.0, 30.0, -120.0, -60.0, 'Colombia & Venezuela'),
(0.0, 30.0, -60.0, 0.0, 'Caribbean Sea (Cuba, Jamaica)'),
(0.0, 30.0, 0.0, 60.0, 'North Africa (Egypt & Libya)'),
(0.0, 30.0, 60.0, 120.0, 'Eastern Mediterranean (Turkey, Cyprus)'),
(0.0, 30.0, 120.0, 180.0, 'Central Asia (Uzbekistan)'),
(30.0, 60.0, -180.0, -120.0, 'North Pacific Ocean'),
(30.0, 60.0, -120.0, -60.0, 'Western United States (California)'),
(30.0, 60.0, -60.0, 0.0, 'Eastern United States'),
(30.0, 60.0, 0.0, 60.0, 'Western Europe (Iberian Peninsula)'),
(30.0, 60.0, 60.0, 120.0, 'Central Europe (France & Germany)'),
(30.0, 60.0, 120.0, 180.0, 'Eastern Russia & Kazakhstan'),
(60.0, 90.0, -180.0, -120.0, 'Arctic Ocean'),
(60.0, 90.0, -120.0, -60.0, 'Alaska & Canada'),
(60.0, 90.0, -60.0, 0.0, 'Northern Europe (Scandinavia)'),
(60.0, 90.0, 0.0, 60.0, 'Northern Europe (Finland & Russia)'),
(60.0, 90.0, 60.0, 120.0, 'Siberia & Eastern Russia'),
(60.0, 90.1, 120.0, 180.1, 'Arctic Ocean & Siberia');