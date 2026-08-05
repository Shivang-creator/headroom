# task04_full_audit — comparison `528799d8c8f8`


## truncate

- outcome: **✓ solved**
- turns: 11
- peak prompt tokens: 13,788
- total input tokens: 94,251
- patches applied: 1
- tool results truncated: 1
- wall time: 91.0s


### Turn-by-turn

| turn | tool | prompt tokens | vs 32,768 |
|---:|---|---:|---|
| 1 | `run_bash` | 940 | 3% |
| 2 | `run_bash` | 1,008 | 3% |
| 3 | `run_bash` | 1,068 | 3% |
| 4 | `next_page` | 8,593 | 26% |
| 5 | `list_dir` | 8,607 | 26% |
| 6 | `read_file` | 8,693 | 27% |
| 7 | `read_file` | 10,959 | 33% |
| 8 | `read_file` | 13,215 | 40% |
| 9 | `apply_patch` | 13,694 | 42% |
| 10 | `run_bash` | 13,686 | 42% |
| 11 | `finish` | 13,788 | 42% |

## paginate

- outcome: **✓ solved**
- turns: 14
- peak prompt tokens: 12,131
- total input tokens: 111,971
- patches applied: 1
- tool results truncated: 0
- wall time: 82.9s


### Turn-by-turn

| turn | tool | prompt tokens | vs 32,768 |
|---:|---|---:|---|
| 1 | `run_bash` | 940 | 3% |
| 2 | `run_bash` | 1,008 | 3% |
| 3 | `run_bash` | 1,069 | 3% |
| 4 | `next_page` | 3,908 | 12% |
| 5 | `list_dir` | 6,776 | 21% |
| 6 | `read_file` | 6,844 | 21% |
| 7 | `read_file` | 9,110 | 28% |
| 8 | `read_file` | 11,325 | 35% |
| 9 | `next_page` | 11,585 | 35% |
| 10 | `next_page` | 11,679 | 36% |
| 11 | `run_bash` | 11,693 | 36% |
| 12 | `apply_patch` | 11,874 | 36% |
| 13 | `run_bash` | 12,029 | 37% |
| 14 | `finish` | 12,131 | 37% |

## paritok

- outcome: **✓ solved**
- turns: 16
- peak prompt tokens: 6,502
- total input tokens: 64,320
- patches applied: 1
- tool results truncated: 0
- wall time: 185.1s

- proxy stats: `{"total_requests": 17, "input_tokens_original": 213549, "input_tokens_compressed": 55688, "tokens_saved": 157861, "compression_ratio": 0.2608}`


### Turn-by-turn

| turn | tool | prompt tokens | vs 32,768 |
|---:|---|---:|---|
| 1 | `run_bash` | 940 | 3% |
| 2 | `run_bash` | 1,008 | 3% |
| 3 | `run_bash` | 1,070 | 3% |
| 4 | `next_page` | 1,560 | 5% |
| 5 | `next_page` | 1,773 | 5% |
| 6 | `next_page` | 2,006 | 6% |
| 7 | `next_page` | 3,507 | 11% |
| 8 | `list_dir` | 4,994 | 15% |
| 9 | `read_file` | 5,087 | 16% |
| 10 | `read_file` | 5,409 | 17% |
| 11 | `read_file` | 5,737 | 18% |
| 12 | `next_page` | 5,990 | 18% |
| 13 | `run_bash` | 6,079 | 19% |
| 14 | `apply_patch` | 6,258 | 19% |
| 15 | `run_bash` | 6,400 | 20% |
| 16 | `finish` | 6,502 | 20% |
