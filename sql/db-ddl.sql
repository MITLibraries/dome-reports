/*
Database DDL in SQLite3 for DOME Collections Reports

-- uuids are always taken from the Postgres database

-- foreign keys are not automatically turned on,
   in any insert scenario, first use the following command:
   PRAGMA foreign_keys = ON;

*/

CREATE TABLE Community (
    uuid         TEXT  PRIMARY KEY,
    name         TEXT  NOT NULL,
    short_name   TEXT  NOT NULL,
    handle       TEXT,
    notes        TEXT
);

CREATE TABLE Collection (
    uuid         TEXT  PRIMARY KEY,
    comm_uuid    TEXT NOT NULL,
    name         TEXT NOT NULL,
    short_name   TEXT NOT NULL,
    reportable   NUMERIC DEFAULT 1  CHECK( reportable IN (0,1)),
    owner        TEXT,
    handle       TEXT,
    notes        TEXT,
    FOREIGN KEY (comm_uuid) REFERENCES Community (uuid)
);

CREATE TABLE Monthly_Item_Count (
    coll_uuid    INTEGER NOT NULL,
    year         INTEGER NOT NULL,     -- dddd
    month        INTEGER NOT NULL,     -- (1..12)
    item_count   INTEGER NOT NULL DEFAULT 0,
    UNIQUE (coll_uuid, year, month),
    FOREIGN KEY (coll_uuid) REFERENCES Collection (uuid)
);

CREATE TABLE FilesProcessed (
    name         TEXT,
    timestamp    TEXT
);

CREATE INDEX idx_comm_uuid ON Collection(comm_uuid);
CREATE INDEX idx_mic_uuid ON Monthly_Item_Count(coll_uuid);
CREATE INDEX idx_fp_name ON FilesProcessed(name);
