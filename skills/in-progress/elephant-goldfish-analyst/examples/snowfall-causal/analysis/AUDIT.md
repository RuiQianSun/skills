# Audit

Ledger head `8a88e26837c3d9fb`. Every recorded result re-executed from its frozen script and sealed data. 0 failure(s).

| check | result | detail |
|---|---|---|
| ledger hash chain | pass | 25 entries |
| explore.csv hash | pass |  |
| holdout.csv hash | pass |  |
| H1 test frozen | pass | analysis/tests/H1.py |
| H2 test frozen | pass | analysis/tests/H2.py |
| H1 holdout result `#6` re-executed | pass | byte-identical |
| V1 test frozen | pass | analysis/tests/V1.py |
| V2 test frozen | pass | analysis/tests/V2.py |
| V1 holdout result `#10` re-executed | pass | byte-identical |
| H1 replication script by goldfish-H1-sonnet unchanged | pass | analysis/goldfish/H1.py |
| H1 replication by goldfish-H1-sonnet `#21` | pass | byte-identical |
| V1 replication script by goldfish-V1-sonnet unchanged | pass | analysis/goldfish/V1.py |
| V1 replication by goldfish-V1-sonnet `#22` | pass | byte-identical |
