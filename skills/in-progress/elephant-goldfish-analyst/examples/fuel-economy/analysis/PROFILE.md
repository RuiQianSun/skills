# Variable profile (explore data)

9754 rows. Suggested roles are a starting point for the conversation with the user, not a decision.

| column | type | distinct | empty | range or top values | suggested role |
|---|---|---|---|---|---|
| id | numeric | 9754 | 0 | 31082 to 44224 | key |
| year | numeric | 8 | 0 | 2012 to 2019 | time |
| make | text | 55 | 0 | BMW, Ford, Chevrolet | feature |
| vclass | text | 24 | 0 | Midsize Cars, Compact Cars, Subcompact Cars | segment |
| drive | text | 5 | 0 | Front-Wheel Drive, Rear-Wheel Drive, All-Wheel Drive | segment |
| transmission | text | 3 | 0 | Automatic, Manual, CVT | segment |
| cylinders | numeric | 8 | 0 | 3 to 16 | feature |
| displ | numeric | 54 | 0 | 0.9 to 8.4 | feature or target |
| turbo | numeric | 2 | 0 | 0 to 1 | feature |
| supercharger | numeric | 2 | 0 | 0 to 1 | feature |
| hybrid | numeric | 2 | 0 | 0 to 1 | feature |
| fuel | text | 4 | 0 | Regular, Premium, Diesel | segment |
| comb_mpg | numeric | 44 | 0 | 10 to 58 | feature or target |
| city_mpg | numeric | 49 | 0 | 8 to 58 | feature or target |
| highway_mpg | numeric | 43 | 0 | 11 to 59 | feature or target |
| co2_g_per_mile | numeric | 537 | 0 | 154 to 888.7 | feature or target |
| annual_fuel_cost | numeric | 67 | 0 | 1000 to 7250 | feature or target |
| barrels_per_year | numeric | 63 | 0 | 5.129 to 29.751 | feature or target |
| five_year_savings | numeric | 67 | 0 | -26000 to 5250 | feature or target |
