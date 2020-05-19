CREATE TABLE "countries" (
	"code"	INTEGER NOT NULL,
	"name"	INTEGER NOT NULL,
	"continent_code"	INTEGER NOT NULL,
	FOREIGN KEY("continent_code") REFERENCES "continents"("code"),
	PRIMARY KEY("code","continent_code")
);

CREATE UNIQUE INDEX "country_code_index" ON "countries" (
	"code"	ASC
);
