# task01_report_mean — comparison `640f82a24989`


## truncate

- outcome: **✓ solved**
- turns: 9
- peak prompt tokens: 7,112
- total input tokens: 30,648
- patches applied: 1
- tool results truncated: 0
- wall time: 22.2s


### Turn-by-turn

| turn | tool | prompt tokens | vs 32,768 |
|---:|---|---:|---|
| 1 | `run_bash` | 826 | 3% |
| 2 | `run_bash` | 901 | 3% |
| 3 | `run_bash` | 952 | 3% |
| 4 | `list_dir` | 1,257 | 4% |
| 5 | `read_file` | 1,388 | 4% |
| 6 | `read_file` | 4,151 | 13% |
| 7 | `apply_patch` | 6,999 | 21% |
| 8 | `run_bash` | 7,062 | 22% |
| 9 | `finish` | 7,112 | 22% |

## paginate

- outcome: **✓ solved**
- turns: 9
- peak prompt tokens: 6,116
- total input tokens: 27,142
- patches applied: 1
- tool results truncated: 0
- wall time: 34.2s


### Turn-by-turn

| turn | tool | prompt tokens | vs 32,768 |
|---:|---|---:|---|
| 1 | `run_bash` | 826 | 3% |
| 2 | `run_bash` | 894 | 3% |
| 3 | `run_bash` | 953 | 3% |
| 4 | `list_dir` | 1,251 | 4% |
| 5 | `read_file` | 1,389 | 4% |
| 6 | `read_file` | 3,658 | 11% |
| 7 | `apply_patch` | 5,996 | 18% |
| 8 | `run_bash` | 6,059 | 18% |
| 9 | `finish` | 6,116 | 19% |

## paritok

- outcome: **✓ solved**
- turns: 9
- peak prompt tokens: 2,079
- total input tokens: 13,225
- patches applied: 1
- tool results truncated: 0
- wall time: 65.7s

- proxy stats: `{"total_requests": 9, "input_tokens_original": 21029, "input_tokens_compressed": 6711, "tokens_saved": 14318, "compression_ratio": 0.3191}`


### Turn-by-turn

| turn | tool | prompt tokens | vs 32,768 |
|---:|---|---:|---|
| 1 | `run_bash` | 826 | 3% |
| 2 | `run_bash` | 894 | 3% |
| 3 | `run_bash` | 954 | 3% |
| 4 | `list_dir` | 1,252 | 4% |
| 5 | `read_file` | 1,390 | 4% |
| 6 | `read_file` | 1,863 | 6% |
| 7 | `apply_patch` | 1,952 | 6% |
| 8 | `run_bash` | 2,015 | 6% |
| 9 | `finish` | 2,079 | 6% |
