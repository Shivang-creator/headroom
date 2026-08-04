# task01_report_mean — pair `297dd2677cbc`


## Paritok OFF

- outcome: **✓ solved**
- turns: 9
- peak prompt tokens: 7,013
- total input tokens: 29,823
- patches applied: 1
- wall time: 17.8s


### Turn-by-turn

| turn | tool | prompt tokens | vs 32,768 |
|---:|---|---:|---|
| 1 | `run_bash` | 746 | 2% |
| 2 | `run_bash` | 821 | 3% |
| 3 | `run_bash` | 874 | 3% |
| 4 | `list_dir` | 1,172 | 4% |
| 5 | `read_file` | 1,296 | 4% |
| 6 | `read_file` | 4,052 | 12% |
| 7 | `apply_patch` | 6,893 | 21% |
| 8 | `run_bash` | 6,956 | 21% |
| 9 | `finish` | 7,013 | 21% |

## Paritok ON

- outcome: **✓ solved**
- turns: 10
- peak prompt tokens: 2,100
- total input tokens: 14,589
- patches applied: 1
- wall time: 17.0s

- proxy stats: `{"total_requests": 10, "input_tokens_original": 37779, "input_tokens_compressed": 7337, "tokens_saved": 30442, "compression_ratio": 0.1942}`


### Turn-by-turn

| turn | tool | prompt tokens | vs 32,768 |
|---:|---|---:|---|
| 1 | `run_bash` | 746 | 2% |
| 2 | `run_bash` | 814 | 2% |
| 3 | `run_bash` | 874 | 3% |
| 4 | `list_dir` | 1,172 | 4% |
| 5 | `read_file` | 1,289 | 4% |
| 6 | `read_file` | 1,763 | 5% |
| 7 | `read_file` | 1,840 | 6% |
| 8 | `apply_patch` | 1,948 | 6% |
| 9 | `run_bash` | 2,043 | 6% |
| 10 | `finish` | 2,100 | 6% |
