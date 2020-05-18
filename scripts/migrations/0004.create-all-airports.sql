CREATE TABLE "all_airports" (
	"code"	TEXT NOT NULL UNIQUE,
	"type"	TEXT NOT NULL,
	"municipality"	TEXT,
	"region_code"	TEXT NOT NULL,
	PRIMARY KEY("code"),
	FOREIGN KEY("region_code") REFERENCES "regions"("code")
);

CREATE INDEX "allairport_code_index" ON "all_airports" (
	"code"	ASC
);
