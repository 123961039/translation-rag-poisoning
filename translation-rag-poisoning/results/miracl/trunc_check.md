# BGE-M3 truncation rate (max_seq_length = 512)

| lang | text | n | median tokens | 95th percentile | fraction > 512 |
|---|---|---|---|---|---|
| sw | poison native/bb | 56 | 34 | 49 | 0.0% |
| sw | poison native/adv | 56 | 23 | 36 | 0.0% |
| sw | poison trans/bb | 88 | 36 | 55 | 0.0% |
| sw | poison trans/adv | 88 | 25 | 38 | 0.0% |
| sw | poison en/bb | 88 | 35 | 50 | 0.0% |
| sw | poison en/adv | 88 | 23 | 36 | 0.0% |
| sw | corpus passages (random) | 5000 | 47 | 159 | 0.2% |
| te | poison native/bb | 51 | 32 | 41 | 0.0% |
| te | poison native/adv | 51 | 20 | 29 | 0.0% |
| te | poison trans/bb | 100 | 40 | 54 | 0.0% |
| te | poison trans/adv | 100 | 27 | 43 | 0.0% |
| te | poison en/bb | 100 | 36 | 43 | 0.0% |
| te | poison en/adv | 100 | 24 | 30 | 0.0% |
| te | corpus passages (random) | 5000 | 95 | 367 | 2.7% |
| yo | poison native/bb | 70 | 42 | 64 | 0.0% |
| yo | poison native/adv | 70 | 25 | 50 | 0.0% |
| yo | poison trans/bb | 80 | 63 | 97 | 0.0% |
| yo | poison trans/adv | 80 | 46 | 77 | 0.0% |
| yo | poison en/bb | 80 | 40 | 58 | 0.0% |
| yo | poison en/adv | 80 | 23 | 37 | 0.0% |
| yo | corpus passages (random) | 5000 | 42 | 291 | 1.4% |
| id | poison native/bb | 40 | 28 | 38 | 0.0% |
| id | poison native/adv | 40 | 19 | 31 | 0.0% |
| id | poison trans/bb | 62 | 32 | 43 | 0.0% |
| id | poison trans/adv | 62 | 23 | 34 | 0.0% |
| id | poison en/bb | 62 | 34 | 50 | 0.0% |
| id | poison en/adv | 62 | 24 | 42 | 0.0% |
| id | corpus passages (random) | 5000 | 64 | 200 | 0.1% |

Truncation affects only texts longer than 512 tokens; when the fraction is near 0, truncation does not affect the comparison of detectors.
