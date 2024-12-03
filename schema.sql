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
    tsunami BOOLEAN,
    felt_report_count SMALLINT,
    cdi DECIMAL,
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
    FOREIGN KEY (type_id) REFERENCES type(type_id)
);

CREATE TABLE users (
    user_id BIGINT GENERATED ALWAYS AS IDENTITY,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(15) UNIQUE NOT NULL,
    PRIMARY KEY (user_id)
);

CREATE TABLE regions (
    region_id BIGINT GENERATED ALWAYS AS IDENTITY,
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
    region_id BIGINT,
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


