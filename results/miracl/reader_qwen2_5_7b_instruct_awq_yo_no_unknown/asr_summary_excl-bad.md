# Generation-level attack success rate (reader Qwen2.5-7B-Instruct-AWQ, rebuilt from JSON; directory reader_qwen2_5_7b_instruct_awq_yo_no_unknown)

| lang | variant | form | condition | questions | ASR | ASR (loose) | accuracy | unknown |
|---|---|---|---|---|---|---|---|---|
| yo | - | - | clean | 26 | 0.04 (0.00–0.12) | 0.08 (0.00–0.19) | 0.54 (0.35–0.73) | 0.00 |
| yo | - | - | clean_defended | 26 | 0.04 (0.00–0.12) | 0.08 (0.00–0.19) | 0.54 (0.35–0.73) | 0.00 |
| yo | en | adv | attacked | 26 | 0.19 (0.04–0.35) | 0.27 (0.12–0.46) | 0.50 (0.31–0.69) | 0.00 |
| yo | en | adv | defended_ideal | 26 | 0.08 (0.00–0.19) | 0.15 (0.04–0.31) | 0.50 (0.31–0.69) | 0.00 |
| yo | en | adv | defended | 26 | 0.08 (0.00–0.19) | 0.15 (0.04–0.31) | 0.50 (0.31–0.69) | 0.00 |
| yo | en | bb | attacked | 26 | 0.46 (0.27–0.65) | 0.46 (0.27–0.65) | 0.19 (0.08–0.38) | 0.00 |
| yo | en | bb | defended_ideal | 26 | 0.27 (0.12–0.46) | 0.27 (0.12–0.46) | 0.23 (0.08–0.38) | 0.00 |
| yo | en | bb | defended | 26 | 0.27 (0.12–0.42) | 0.27 (0.12–0.46) | 0.23 (0.08–0.38) | 0.00 |
| yo | native | adv | attacked | 24 | 0.46 (0.25–0.67) | 0.54 (0.33–0.75) | 0.21 (0.04–0.38) | 0.00 |
| yo | native | adv | defended_ideal | 24 | 0.21 (0.04–0.38) | 0.25 (0.08–0.42) | 0.38 (0.21–0.58) | 0.00 |
| yo | native | adv | defended | 24 | 0.21 (0.08–0.38) | 0.25 (0.08–0.42) | 0.38 (0.17–0.58) | 0.00 |
| yo | native | bb | attacked | 24 | 0.67 (0.46–0.83) | 0.75 (0.58–0.92) | 0.21 (0.08–0.38) | 0.00 |
| yo | native | bb | defended_ideal | 24 | 0.21 (0.04–0.38) | 0.25 (0.08–0.42) | 0.42 (0.21–0.58) | 0.00 |
| yo | native | bb | defended | 24 | 0.21 (0.04–0.38) | 0.25 (0.08–0.42) | 0.42 (0.25–0.62) | 0.00 |
| yo | trans | adv | attacked | 26 | 0.15 (0.04–0.31) | 0.19 (0.04–0.38) | 0.42 (0.23–0.62) | 0.00 |
| yo | trans | adv | defended_ideal | 26 | 0.08 (0.00–0.19) | 0.15 (0.04–0.31) | 0.46 (0.27–0.65) | 0.00 |
| yo | trans | adv | defended | 26 | 0.08 (0.00–0.19) | 0.15 (0.04–0.31) | 0.46 (0.27–0.65) | 0.00 |
| yo | trans | bb | attacked | 26 | 0.50 (0.31–0.69) | 0.50 (0.31–0.69) | 0.04 (0.00–0.12) | 0.00 |
| yo | trans | bb | defended_ideal | 26 | 0.31 (0.12–0.50) | 0.31 (0.15–0.50) | 0.23 (0.08–0.38) | 0.00 |
| yo | trans | bb | defended | 26 | 0.31 (0.15–0.50) | 0.31 (0.15–0.50) | 0.19 (0.08–0.35) | 0.00 |

## Actual cost of false alarms (without attack)

| lang | retrieved benign passages flagged | gold wrongly removed |
|---|---|---|
| yo | 5.4% | 2/34 |
