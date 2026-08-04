# task03_verbose_suite — pair `dc45296ad397`


## Paritok OFF

- outcome: **✓ solved**
- turns: 9
- peak prompt tokens: 8,716
- total input tokens: 48,708
- patches applied: 1
- wall time: 30.8s


### Turn-by-turn

| turn | tool | prompt tokens | vs 32,768 |
|---:|---|---:|---|
| 1 | `run_bash` | 868 | 3% |
| 2 | `list_dir` | 3,704 | 11% |
| 3 | `read_file` | 3,784 | 12% |
| 4 | `read_file` | 4,030 | 12% |
| 5 | `read_file` | 4,077 | 12% |
| 6 | `read_file` | 6,343 | 19% |
| 7 | `apply_patch` | 8,557 | 26% |
| 8 | `run_bash` | 8,629 | 26% |
| 9 | `finish` | 8,716 | 27% |

## Paritok ON

- outcome: **✓ solved**
- turns: 10
- peak prompt tokens: 4,388
- total input tokens: 35,093
- patches applied: 1
- wall time: 111.2s

- proxy stats: `{"total_requests": 10, "input_tokens_original": 46500, "input_tokens_compressed": 24286, "tokens_saved": 22214, "compression_ratio": 0.5223}`


### Turn-by-turn

| turn | tool | prompt tokens | vs 32,768 |
|---:|---|---:|---|
| 1 | `run_bash` | 868 | 3% |
| 2 | `run_bash` | 2,906 | 9% |
| 3 | `list_dir` | 3,397 | 10% |
| 4 | `read_file` | 3,470 | 11% |
| 5 | `read_file` | 3,723 | 11% |
| 6 | `read_file` | 3,770 | 12% |
| 7 | `read_file` | 4,092 | 12% |
| 8 | `apply_patch` | 4,178 | 13% |
| 9 | `run_bash` | 4,301 | 13% |
| 10 | `finish` | 4,388 | 13% |
