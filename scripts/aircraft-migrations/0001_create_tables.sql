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
	"name"	TEXT NOT NULL,
	"base"	INTEGER,
	FOREIGN KEY("aircraft_id") REFERENCES "aircraft"("id")
);
DROP TABLE IF EXISTS "tags";
CREATE TABLE IF NOT EXISTS "tags" (
	"id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	"name"	TEXT NOT NULL UNIQUE,
	"count"	INTEGER
);
CREATE INDEX "tag_name_index" ON "tags" (
	"name"	ASC
);
DROP TABLE IF EXISTS "status";
CREATE TABLE IF NOT EXISTS "status" (
	"id"	INTEGER NOT NULL UNIQUE,
	"name"	TEXT NOT NULL UNIQUE,
	PRIMARY KEY("id")
);
INSERT INTO "status" ("id","name") VALUES (0,'Development');
INSERT INTO "status" ("id","name") VALUES (1,'Alpha');
INSERT INTO "status" ("id","name") VALUES (2,'Beta');
INSERT INTO "status" ("id","name") VALUES (3,'Early Production');
INSERT INTO "status" ("id","name") VALUES (4,'Production');
INSERT INTO "status" ("id","name") VALUES (5,'Advanced Production');
DROP TABLE IF EXISTS "aircraft";
CREATE TABLE IF NOT EXISTS "aircraft" (
	"id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	"name"	TEXT NOT NULL UNIQUE,
	"description"	TEXT NOT NULL,
	"status_id"	INTEGER NOT NULL,
	"rating_fdm"	INTEGER,
	"rating_systems"	INTEGER,
	"rating_model"	INTEGER,
	"rating_cockpit"	INTEGER,
	FOREIGN KEY("status_id") REFERENCES "status"("id")
);
CREATE TABLE "meta" (
	"key"	TEXT NOT NULL UNIQUE,
	"value"	TEXT,
	PRIMARY KEY("key")
);
