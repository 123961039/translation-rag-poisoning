# Generation-level attack success rate (reader Qwen3-14B-AWQ, rebuilt from JSON; directory reader_qwen3_14b_yo_no_unknown)

| lang | variant | form | condition | questions | ASR | ASR (loose) | accuracy | unknown |
|---|---|---|---|---|---|---|---|---|
| yo | - | - | clean | 26 | 0.00 (0.00–0.00) | 0.00 (0.00–0.00) | 0.62 (0.42–0.81) | 0.00 |
| yo | - | - | clean_defended | 26 | 0.00 (0.00–0.00) | 0.00 (0.00–0.00) | 0.54 (0.35–0.73) | 0.00 |
| yo | en | adv | attacked | 26 | 0.23 (0.08–0.38) | 0.23 (0.08–0.38) | 0.50 (0.31–0.69) | 0.00 |
| yo | en | adv | defended_ideal | 26 | 0.04 (0.00–0.12) | 0.04 (0.00–0.12) | 0.58 (0.38–0.77) | 0.00 |
| yo | en | adv | defended | 26 | 0.04 (0.00–0.12) | 0.04 (0.00–0.12) | 0.50 (0.31–0.69) | 0.00 |
| yo | en | bb | attacked | 26 | 0.73 (0.58–0.88) | 0.73 (0.58–0.88) | 0.15 (0.04–0.31) | 0.00 |
| yo | en | bb | defended_ideal | 26 | 0.38 (0.19–0.58) | 0.38 (0.19–0.54) | 0.38 (0.19–0.58) | 0.00 |
| yo | en | bb | defended | 26 | 0.38 (0.19–0.58) | 0.38 (0.19–0.58) | 0.31 (0.15–0.46) | 0.00 |
| yo | native | adv | attacked | 24 | 0.42 (0.25–0.62) | 0.46 (0.25–0.63) | 0.38 (0.21–0.58) | 0.00 |
| yo | native | adv | defended_ideal | 24 | 0.12 (0.00–0.25) | 0.17 (0.04–0.33) | 0.58 (0.38–0.79) | 0.00 |
| yo | native | adv | defended | 24 | 0.12 (0.00–0.25) | 0.17 (0.04–0.33) | 0.50 (0.29–0.71) | 0.00 |
| yo | native | bb | attacked | 24 | 0.71 (0.50–0.88) | 0.75 (0.58–0.92) | 0.12 (0.00–0.29) | 0.00 |
| yo | native | bb | defended_ideal | 24 | 0.08 (0.00–0.21) | 0.08 (0.00–0.21) | 0.50 (0.29–0.71) | 0.00 |
| yo | native | bb | defended | 24 | 0.08 (0.00–0.21) | 0.08 (0.00–0.21) | 0.42 (0.21–0.62) | 0.00 |
| yo | trans | adv | attacked | 26 | 0.04 (0.00–0.12) | 0.04 (0.00–0.12) | 0.65 (0.46–0.81) | 0.00 |
| yo | trans | adv | defended_ideal | 26 | 0.00 (0.00–0.00) | 0.00 (0.00–0.00) | 0.62 (0.42–0.81) | 0.00 |
| yo | trans | adv | defended | 26 | 0.00 (0.00–0.00) | 0.00 (0.00–0.00) | 0.54 (0.35–0.73) | 0.00 |
| yo | trans | bb | attacked | 26 | 0.50 (0.31–0.69) | 0.54 (0.35–0.73) | 0.19 (0.04–0.35) | 0.00 |
| yo | trans | bb | defended_ideal | 26 | 0.19 (0.04–0.35) | 0.23 (0.08–0.38) | 0.50 (0.31–0.69) | 0.00 |
| yo | trans | bb | defended | 26 | 0.19 (0.08–0.35) | 0.23 (0.08–0.38) | 0.46 (0.27–0.69) | 0.00 |

## Actual cost of false alarms (without attack)

| lang | retrieved benign passages flagged | gold wrongly removed |
|---|---|---|
| yo | 5.4% | 2/34 |
