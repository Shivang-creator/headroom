# task02_pipeline_triage — pair `088934e8e842`


## Paritok OFF

- outcome: **✓ solved**
- turns: 15
- peak prompt tokens: 12,116
- total input tokens: 91,281
- patches applied: 3
- wall time: 65.7s


### Turn-by-turn

| turn | tool | prompt tokens | vs 32,768 |
|---:|---|---:|---|
| 1 | `run_bash` | 746 | 2% |
| 2 | `run_bash` | 814 | 2% |
| 3 | `run_bash` | 876 | 3% |
| 4 | `read_file` | 1,554 | 5% |
| 5 | `list_dir` | 1,981 | 6% |
| 6 | `read_file` | 2,254 | 7% |
| 7 | `read_file` | 2,301 | 7% |
| 8 | `read_file` | 4,671 | 14% |
| 9 | `read_file` | 7,026 | 21% |
| 10 | `read_file` | 9,352 | 29% |
| 11 | `apply_patch` | 11,664 | 36% |
| 12 | `apply_patch` | 11,893 | 36% |
| 13 | `apply_patch` | 11,974 | 37% |
| 14 | `run_bash` | 12,059 | 37% |
| 15 | `finish` | 12,116 | 37% |

## Paritok ON

- outcome: **✓ solved**
- turns: 16
- peak prompt tokens: 5,146
- total input tokens: 37,308
- patches applied: 3
- wall time: 80.7s

- proxy stats: `{"total_requests": 16, "input_tokens_original": 86256, "input_tokens_compressed": 15879, "tokens_saved": 70377, "compression_ratio": 0.1841}`


### Turn-by-turn

| turn | tool | prompt tokens | vs 32,768 |
|---:|---|---:|---|
| 1 | `run_bash` | 746 | 2% |
| 2 | `run_bash` | 814 | 2% |
| 3 | `run_bash` | 876 | 3% |
| 4 | `read_file` | 2,055 | 6% |
| 5 | `list_dir` | 1,802 | 5% |
| 6 | `read_file` | 2,075 | 6% |
| 7 | `read_file` | 2,122 | 6% |
| 8 | `read_file` | 2,260 | 7% |
| 9 | `read_file` | 2,362 | 7% |
| 10 | `read_file` | 2,485 | 8% |
| 11 | `apply_patch` | 2,585 | 8% |
| 12 | `apply_patch` | 5,146 | 16% |
| 13 | `apply_patch` | 2,904 | 9% |
| 14 | `apply_patch` | 2,959 | 9% |
| 15 | `run_bash` | 3,030 | 9% |
| 16 | `finish` | 3,087 | 9% |
