Airfield selector dataload / update:

Initial creation of database?

a) distribute a seed database, created by a script and copy it when a working one is not found

- migrations:
  b)

Is an update needed?

1. download `https://sourceforge.net/p/flightgear/fgdata/ci/next/log/?path=/Airports/apt.dat.gz`
2. find text of first link with "rev" class, if it's different from what is in settings then yes `<a class="rev" href="/p/flightgear/fgdata/ci/07fdf028615042dccd555b4be5dccabf2609faf0/">[07fdf0]</a>`

How to update?

Download, decompress and parse over `https://sourceforge.net/p/flightgear/fgdata/ci/next/tree/Airports/apt.dat.gz?format=raw`:

1. lines starting `1 ...` declare a new airport:

`1 433 1 0 YMML Melbourne Intl`

- only info avaiable is code, and name/desc

2. lines starting `100 ...` and `101 ...` declare a runway pair

```
100   45.11   1   1 0.00 1 2 1 16  -37.65286600  144.83484400   29.87    0.00 4  4 1 0 34  -37.68536800  144.84133600   29.87    0.00 4 11 0 0
100   x   x   x x x x x <rwy>  <lat>  <lon>   x    x x  x x x <rwy-rcp>  <rcp-lat>  <rcp-lon>   x    x x x x x
101   30.48 0 19   39.13740056 -084.82783540 01   39.12759944 -084.82938684
101   x x <rwy>   <lat> <lon> <rwy-rcp>  <rcp-lat>  <rcp-lon>
```

3. lines starting `102 ...` declare a helipad

```
102 H<num>   <lat>  <lon>  <num>   <num>   <num>   <int> <bool>   <bool> <num> <bool>
```

4. write out a table with the following:

# start_points

id|icao_code|continent_code|country_code|region_code|description|type|heading|lat|lon

type:

- runway
- helipad

other tables:

# continents

code
name

# countries

code
name

# regions

code
name

datasources:
https://datahub.io/core/continent-codes
https://datahub.io/core/country-list
https://datahub.io/core/airport-codes
