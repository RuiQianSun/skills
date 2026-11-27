# Variable profile (explore data)

80 rows. Suggested roles are a starting point for the conversation with the user, not a decision.

| column | type | distinct | empty | range or top values | suggested role |
|---|---|---|---|---|---|
| year | numeric | 8 | 0 | 2010 to 2017 | time |
| province | text | 10 | 0 | nl, pe, ns | segment |
| apr_sales | numeric | 80 | 0 | 2509 to 230324 | key |
| may_sales | numeric | 80 | 0 | 2648 to 240712 | key |
| oct_sales | numeric | 80 | 0 | 2564 to 251952 | key |
| nov_sales | numeric | 80 | 0 | 3009 to 291285 | key |
| apr_share | numeric | 77 | 0 | 0.4171 to 0.5678 | feature or target |
| oct_share | numeric | 76 | 0 | 0.415 to 0.5472 | feature or target |
| fall_7c_day | numeric | 41 | 0 | 255 to 333 | feature or target |
| first_snow_day | numeric | 42 | 17 | 251 to 362 | feature or target |
| sep_mean_temp | numeric | 74 | 0 | 9.29 to 19.69 | feature or target |
| oct_mean_temp | numeric | 76 | 0 | 1.97 to 13.29 | feature or target |
| spring_7c_day | numeric | 43 | 0 | 46 to 154 | feature or target |
| mar_mean_temp | numeric | 77 | 0 | -12.66 to 8.45 | feature or target |
| apr_mean_temp | numeric | 74 | 0 | -3.56 to 11.78 | feature or target |
| fall_days_with_weather | numeric | 10 | 0 | 90 to 108 | feature |
