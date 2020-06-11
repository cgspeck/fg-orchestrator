DROP TABLE IF EXISTS "web_panels";
CREATE TABLE IF NOT EXISTS "web_panels" (
	"id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	"aircraft_id"	INTEGER,
	"name"	TEXT NOT NULL,
	"path"	INTEGER,
	FOREIGN KEY("aircraft_id") REFERENCES "aircraft"("id")
);
