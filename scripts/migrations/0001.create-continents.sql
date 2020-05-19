CREATE TABLE "continents" (
	"code"	TEXT NOT NULL UNIQUE,
	"name"	TEXT NOT NULL,
	PRIMARY KEY("code")
);
INSERT INTO "continents" ("code","name") VALUES ('AF','Africa');
INSERT INTO "continents" ("code","name") VALUES ('NA','North America');
INSERT INTO "continents" ("code","name") VALUES ('OC','Oceania');
INSERT INTO "continents" ("code","name") VALUES ('AN','Antarctica');
INSERT INTO "continents" ("code","name") VALUES ('AS','Asia');
INSERT INTO "continents" ("code","name") VALUES ('EU','Europe');
INSERT INTO "continents" ("code","name") VALUES ('SA','South America');

CREATE UNIQUE INDEX "continent_code_index" ON "continents" (
	"code"	ASC
);
