# Audit

Ledger head `f37362f6bac9fb6d`. Every recorded result re-executed from its frozen script and sealed data. 0 failure(s).

| check | result | detail |
|---|---|---|
| ledger hash chain | pass | 73 entries |
| explore.csv hash | pass |  |
| holdout.csv hash | pass |  |
| D1 test frozen | pass | analysis/tests/D1.py |
| D1 critic review | pass | analysis/reviews/descriptive.md |
| D2 test frozen | pass | analysis/tests/D2.py |
| D2 critic review | pass | analysis/reviews/descriptive.md |
| D3 test frozen | pass | analysis/tests/D3.py |
| D3 critic review | pass | analysis/reviews/descriptive.md |
| D1 holdout result `#7` re-executed | pass | byte-identical |
| D2 holdout result `#9` re-executed | pass | byte-identical |
| D3 holdout result `#11` re-executed | pass | byte-identical |
| D1 replication script by goldfish-D1-sonnet unchanged | pass | analysis/goldfish/D1.py |
| D1 replication by goldfish-D1-sonnet `#14` | pass | byte-identical |
| D2 replication script by goldfish-D2 unchanged | pass | analysis/goldfish/D2.py |
| D2 replication by goldfish-D2 `#15` | pass | byte-identical |
| D3 replication script by goldfish-D3-sonnet unchanged | pass | analysis/goldfish/D3.py |
| D3 replication by goldfish-D3-sonnet `#16` | pass | byte-identical |
| G1 test frozen | pass | analysis/tests/G1.py |
| G1 critic review | pass | analysis/reviews/diagnostic.md |
| G2 test frozen | pass | analysis/tests/G2.py |
| G2 critic review | pass | analysis/reviews/diagnostic.md |
| G1 holdout result `#19` re-executed | pass | byte-identical |
| G2 holdout result `#21` re-executed | pass | byte-identical |
| G1 replication script by goldfish-G1-sonnet unchanged | pass | analysis/goldfish/G1.py |
| G1 replication by goldfish-G1-sonnet `#26` | pass | byte-identical |
| G2 replication script by goldfish-G2 unchanged | pass | analysis/goldfish/G2.py |
| G2 replication by goldfish-G2 `#27` | pass | byte-identical |
| F1 test frozen | pass | analysis/tests/F1.py |
| F1 critic review | pass | analysis/reviews/predictive.md |
| F1 holdout result `#29` re-executed | pass | byte-identical |
| P1b test frozen | pass | analysis/tests/P1b.py |
| P1b critic review | pass | analysis/reviews/predictive.md |
| P1b holdout result `#38` re-executed | pass | byte-identical |
| F1 replication script by goldfish-F1-sonnet unchanged | pass | analysis/goldfish/F1.py |
| F1 replication by goldfish-F1-sonnet `#41` | pass | byte-identical |
| P1b replication script by goldfish-P1b unchanged | pass | analysis/goldfish/P1b.py |
| P1b replication by goldfish-P1b `#42` | pass | byte-identical |
| referee report by referee-1 | pass | analysis/reviews/referee-1.md |
| G2r test frozen | pass | analysis/tests/G2r.py |
| G2r critic review | pass | analysis/reviews/referee-1.md |
| G2r holdout result `#46` re-executed | pass | byte-identical |
| F1r test frozen | pass | analysis/tests/F1r.py |
| F1r critic review | pass | analysis/reviews/referee-1.md |
| F1r holdout result `#51` re-executed | pass | byte-identical |
| P1r test frozen | pass | analysis/tests/P1r.py |
| P1r critic review | pass | analysis/reviews/referee-1.md |
| P1r holdout result `#56` re-executed | pass | byte-identical |
| G2r replication script by goldfish-G2r-sonnet unchanged | pass | analysis/goldfish/G2r.py |
| G2r replication by goldfish-G2r-sonnet `#59` | pass | byte-identical |
| F1r replication script by goldfish-F1r unchanged | pass | analysis/goldfish/F1r.py |
| F1r replication by goldfish-F1r `#60` | pass | byte-identical |
| P1r replication script by goldfish-P1r-sonnet unchanged | pass | analysis/goldfish/P1r.py |
| P1r replication by goldfish-P1r-sonnet `#61` | pass | byte-identical |
| response to referee-1 | pass | analysis/reviews/response-1.md |
