CREATE TABLE "regions" (
	"code"	TEXT NOT NULL,
	"name"	TEXT NOT NULL,
	"country_code"	INTEGER NOT NULL,
	FOREIGN KEY("country_code") REFERENCES "countries"("code"),
	PRIMARY KEY("code","country_code")
);

CREATE INDEX "region_code_index" ON "regions" (
	"code"	ASC
);
