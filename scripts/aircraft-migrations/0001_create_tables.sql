DROP TABLE IF EXISTS "aircraft_tags";
CREATE TABLE IF NOT EXISTS "aircraft_tags" (
	"id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	"tag_id"	INTEGER NOT NULL,
	"aircraft_id"	INTEGER NOT NULL,
	FOREIGN KEY("tag_id") REFERENCES "tags"("id"),
	FOREIGN KEY("aircraft_id") REFERENCES "aircraft"("id")
);
DROP TABLE IF EXISTS "variants";
CREATE TABLE IF NOT EXISTS "variants" (
	"id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	"aircraft_id"	INTEGER,
	"description"	TEXT NOT NULL,
	FOREIGN KEY("aircraft_id") REFERENCES "aircraft"("id")
);
DROP TABLE IF EXISTS "tags";
CREATE TABLE IF NOT EXISTS "tags" (
	"id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	"name"	TEXT NOT NULL,
	"count"	INTEGER
);
DROP TABLE IF EXISTS "aircraft";
CREATE TABLE IF NOT EXISTS "aircraft" (
	"id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	"description"	TEXT NOT NULL,
	"status"	TEXT,
	"rating_fdm"	INTEGER,
	"rating_systems"	INTEGER,
	"rating_model"	INTEGER,
	"rating_cockpit"	INTEGER
);
