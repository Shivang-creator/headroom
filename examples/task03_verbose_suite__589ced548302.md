# task03_verbose_suite — pair `589ced548302`


## Paritok OFF

- outcome: **✗ overflow at turn 2**
- turns: 2
- peak prompt tokens: 38,442
- total input tokens: 39,230
- patches applied: 0
- wall time: 3.7s


### Turn-by-turn

| turn | tool | prompt tokens | vs 32,768 |
|---:|---|---:|---|
| 1 | `run_bash` | 788 | 2% |
| 2 | `—` | 38,442 | 117% |

## Paritok ON

- outcome: **✗ overflow at turn 2**
- turns: 2
- peak prompt tokens: 38,435
- total input tokens: 39,223
- patches applied: 0
- wall time: 5.7s

- proxy stats: `{"total_requests": 2, "input_tokens_original": 1012, "input_tokens_compressed": 1012, "tokens_saved": 0, "compression_ratio": 1.0}`


### Turn-by-turn

| turn | tool | prompt tokens | vs 32,768 |
|---:|---|---:|---|
| 1 | `run_bash` | 788 | 2% |
| 2 | `—` | 38,435 | 117% |
