# task03_verbose_suite — pair `9284da7bbe1a`


## Paritok OFF

- outcome: **✓ solved**
- turns: 11
- peak prompt tokens: 7,184
- total input tokens: 38,025
- patches applied: 1
- wall time: 24.4s


### Turn-by-turn

| turn | tool | prompt tokens | vs 32,768 |
|---:|---|---:|---|
| 1 | `run_bash` | 743 | 2% |
| 2 | `run_bash` | 819 | 2% |
| 3 | `run_bash` | 887 | 3% |
| 4 | `read_file` | 2,148 | 7% |
| 5 | `list_dir` | 2,401 | 7% |
| 6 | `read_file` | 2,452 | 7% |
| 7 | `read_file` | 2,499 | 8% |
| 8 | `read_file` | 4,772 | 15% |
| 9 | `apply_patch` | 7,024 | 21% |
| 10 | `run_bash` | 7,096 | 22% |
| 11 | `finish` | 7,184 | 22% |

## Paritok ON

- outcome: **✓ solved**
- turns: 11
- peak prompt tokens: 4,833
- total input tokens: 23,946
- patches applied: 1
- wall time: 53.6s

- proxy stats: `{"total_requests": 11, "input_tokens_original": 31175, "input_tokens_compressed": 14056, "tokens_saved": 17119, "compression_ratio": 0.4509}`


### Turn-by-turn

| turn | tool | prompt tokens | vs 32,768 |
|---:|---|---:|---|
| 1 | `run_bash` | 743 | 2% |
| 2 | `run_bash` | 819 | 2% |
| 3 | `run_bash` | 880 | 3% |
| 4 | `read_file` | 1,983 | 6% |
| 5 | `list_dir` | 2,243 | 7% |
| 6 | `read_file` | 2,287 | 7% |
| 7 | `read_file` | 2,334 | 7% |
| 8 | `read_file` | 2,456 | 7% |
| 9 | `apply_patch` | 4,833 | 15% |
| 10 | `run_bash` | 2,640 | 8% |
| 11 | `finish` | 2,728 | 8% |
