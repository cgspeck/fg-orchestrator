CREATE TABLE "runways" (
	"id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	"airport_code"	TEXT NOT NULL,
	"airport_name"	TEXT NOT NULL,
	"location"	TEXT NOT NULL,
	"fg_type_code"	INTEGER NOT NULL,
	"lat"	NUMERIC NOT NULL,
	"lon"	NUMERIC NOT NULL,
	"municipality"	TEXT,
	"region_code"	TEXT NOT NULL,
	"country_code"	TEXT NOT NULL,
	"continent_code"	TEXT NOT NULL,
	FOREIGN KEY("country_code") REFERENCES "countries"("code"),
	FOREIGN KEY("region_code") REFERENCES "regions"("code"),
	FOREIGN KEY("airport_code") REFERENCES "all_airports"("code")
);

CREATE INDEX "runways_airport_code" ON "runways" (
	"airport_code"	ASC
);

CREATE INDEX "runways_airport_name" ON "runways" (
	"airport_name"	ASC
);

CREATE INDEX "runways_region_code" ON "runways" (
	"region_code"	ASC
);

CREATE INDEX "runways_country_code" ON "runways" (
	"country_code"	ASC
);

CREATE INDEX "runways_continent_code" ON "runways" (
	"continent_code"	ASC
);
