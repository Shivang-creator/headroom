# task03_verbose_suite — comparison `4763f289b40d`


## truncate

- outcome: **✓ solved**
- turns: 9
- peak prompt tokens: 13,546
- total input tokens: 86,739
- patches applied: 1
- tool results truncated: 1
- wall time: 78.7s


### Turn-by-turn

| turn | tool | prompt tokens | vs 32,768 |
|---:|---|---:|---|
| 1 | `run_bash` | 868 | 3% |
| 2 | `list_dir` | 8,415 | 26% |
| 3 | `read_file` | 8,500 | 26% |
| 4 | `read_file` | 8,753 | 27% |
| 5 | `read_file` | 8,800 | 27% |
| 6 | `read_file` | 11,066 | 34% |
| 7 | `apply_patch` | 13,325 | 41% |
| 8 | `run_bash` | 13,466 | 41% |
| 9 | `finish` | 13,546 | 41% |

## paginate

- outcome: **✓ solved**
- turns: 9
- peak prompt tokens: 8,816
- total input tokens: 48,901
- patches applied: 1
- tool results truncated: 0
- wall time: 43.3s


### Turn-by-turn

| turn | tool | prompt tokens | vs 32,768 |
|---:|---|---:|---|
| 1 | `run_bash` | 868 | 3% |
| 2 | `list_dir` | 3,704 | 11% |
| 3 | `read_file` | 3,777 | 12% |
| 4 | `read_file` | 4,030 | 12% |
| 5 | `read_file` | 4,077 | 12% |
| 6 | `read_file` | 6,343 | 19% |
| 7 | `apply_patch` | 8,557 | 26% |
| 8 | `run_bash` | 8,729 | 27% |
| 9 | `finish` | 8,816 | 27% |

## paritok

- outcome: **✓ solved**
- turns: 13
- peak prompt tokens: 6,111
- total input tokens: 43,054
- patches applied: 1
- tool results truncated: 0
- wall time: 48.8s

- proxy stats: `{"total_requests": 13, "input_tokens_original": 51002, "input_tokens_compressed": 27894, "tokens_saved": 23108, "compression_ratio": 0.5469}`


### Turn-by-turn

| turn | tool | prompt tokens | vs 32,768 |
|---:|---|---:|---|
| 1 | `run_bash` | 868 | 3% |
| 2 | `run_bash` | 936 | 3% |
| 3 | `run_bash` | 997 | 3% |
| 4 | `list_dir` | 5,871 | 18% |
| 5 | `read_file` | 3,093 | 9% |
| 6 | `list_dir` | 3,109 | 9% |
| 7 | `read_file` | 3,182 | 10% |
| 8 | `read_file` | 3,435 | 10% |
| 9 | `read_file` | 3,482 | 11% |
| 10 | `read_file` | 3,804 | 12% |
| 11 | `apply_patch` | 6,111 | 19% |
| 12 | `run_bash` | 4,036 | 12% |
| 13 | `finish` | 4,130 | 13% |
