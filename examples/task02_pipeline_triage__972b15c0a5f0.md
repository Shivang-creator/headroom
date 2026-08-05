# task02_pipeline_triage — comparison `972b15c0a5f0`


## truncate

- outcome: **✓ solved**
- turns: 15
- peak prompt tokens: 12,208
- total input tokens: 92,518
- patches applied: 3
- tool results truncated: 0
- wall time: 56.0s


### Turn-by-turn

| turn | tool | prompt tokens | vs 32,768 |
|---:|---|---:|---|
| 1 | `run_bash` | 826 | 3% |
| 2 | `run_bash` | 894 | 3% |
| 3 | `run_bash` | 954 | 3% |
| 4 | `read_file` | 1,632 | 5% |
| 5 | `list_dir` | 2,059 | 6% |
| 6 | `read_file` | 2,332 | 7% |
| 7 | `read_file` | 2,386 | 7% |
| 8 | `read_file` | 4,749 | 14% |
| 9 | `read_file` | 7,104 | 22% |
| 10 | `read_file` | 9,430 | 29% |
| 11 | `apply_patch` | 11,742 | 36% |
| 12 | `apply_patch` | 11,985 | 37% |
| 13 | `apply_patch` | 12,066 | 37% |
| 14 | `run_bash` | 12,151 | 37% |
| 15 | `finish` | 12,208 | 37% |

## paginate

- outcome: **✓ solved**
- turns: 15
- peak prompt tokens: 11,994
- total input tokens: 91,167
- patches applied: 3
- tool results truncated: 0
- wall time: 79.9s


### Turn-by-turn

| turn | tool | prompt tokens | vs 32,768 |
|---:|---|---:|---|
| 1 | `run_bash` | 826 | 3% |
| 2 | `run_bash` | 894 | 3% |
| 3 | `run_bash` | 955 | 3% |
| 4 | `read_file` | 1,633 | 5% |
| 5 | `list_dir` | 2,067 | 6% |
| 6 | `read_file` | 2,333 | 7% |
| 7 | `read_file` | 2,380 | 7% |
| 8 | `read_file` | 4,679 | 14% |
| 9 | `read_file` | 7,024 | 21% |
| 10 | `read_file` | 9,279 | 28% |
| 11 | `apply_patch` | 11,543 | 35% |
| 12 | `apply_patch` | 11,771 | 36% |
| 13 | `apply_patch` | 11,852 | 36% |
| 14 | `run_bash` | 11,937 | 36% |
| 15 | `finish` | 11,994 | 37% |

## paritok

- outcome: **✓ solved**
- turns: 17
- peak prompt tokens: 5,306
- total input tokens: 43,808
- patches applied: 3
- tool results truncated: 0
- wall time: 186.6s

- proxy stats: `{"total_requests": 17, "input_tokens_original": 95969, "input_tokens_compressed": 18612, "tokens_saved": 77357, "compression_ratio": 0.1939}`


### Turn-by-turn

| turn | tool | prompt tokens | vs 32,768 |
|---:|---|---:|---|
| 1 | `run_bash` | 826 | 3% |
| 2 | `run_bash` | 894 | 3% |
| 3 | `run_bash` | 956 | 3% |
| 4 | `read_file` | 2,152 | 7% |
| 5 | `list_dir` | 1,906 | 6% |
| 6 | `read_file` | 2,172 | 7% |
| 7 | `read_file` | 2,226 | 7% |
| 8 | `read_file` | 2,356 | 7% |
| 9 | `read_file` | 2,460 | 8% |
| 10 | `read_file` | 2,620 | 8% |
| 11 | `—` | 2,719 | 8% |
| 12 | `apply_patch` | 2,748 | 8% |
| 13 | `apply_patch` | 5,187 | 16% |
| 14 | `apply_patch` | 5,306 | 16% |
| 15 | `apply_patch` | 3,023 | 9% |
| 16 | `run_bash` | 3,100 | 9% |
| 17 | `finish` | 3,157 | 10% |
