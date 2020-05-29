-- #     [index, type, name, number, airlineCodes],
CREATE TABLE "parking" (
	"id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	"airport_code"	TEXT NOT NULL,
	"index"	INTEGER NOT NULL,
	"type"	TEXT NOT NULL,
	"name"	TEXT NOT NULL,
	"number"	TEXT,
	"airline_codes"	TEXT,
	"has_airline_codes"	INTEGER NOT NULL,
	FOREIGN KEY("airport_code") REFERENCES "all_airports"("code")
);

CREATE INDEX "parking_airport_code" ON "parking" (
	"airport_code"	ASC
);

CREATE INDEX "parking_airport_name" ON "parking" (
	"has_airline_codes"	ASC
);
