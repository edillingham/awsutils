DROP TABLE IF EXISTS Servers;

CREATE TABLE Servers (
    instance_id VARCHAR(32),
    private_ip_address VARCHAR(16),
    name VARCHAR(128),
    key_name VARCHAR(64),
    role VARCHAR(16)
);