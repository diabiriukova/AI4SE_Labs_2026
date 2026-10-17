# Final report

## Executive summary

Three prompt formulations were evaluated with the same underlying task: generate one
SQLite query for each of 155 natural-language restaurant questions. The frameworks
were:

- **RTF** — Role, Task, Format
- **RACE** — Role, Action, Context, Expectation
- **ICIO** — Instruction, Context, Input, Output

The original metric is execution accuracy: a prediction is correct only when its
executed result has the same multiset of rows as the expected result. The new metric
is answerability rate: the percentage of predictions that are not the explicit
abstention `SELECT NULL;`.

RACE is the best overall option in this experiment. It had the highest execution
accuracy (27.74%), the highest answerability rate (98.06%), and the shortest
recorded runtime (56 seconds). ICIO was close to RACE in accuracy but took much
longer. RTF was the most conservative framework and had the lowest accuracy and
answerability.

## Results

### Original execution metric

| Framework | Correct | Total | Accuracy | Runtime | Rank by accuracy |
|---|---:|---:|---:|---:|---:|
| RTF | 34 | 155 | 21.94% | 1m 29s | 3 |
| RACE | 43 | 155 | 27.74% | 56s | 1 |
| ICIO | 41 | 155 | 26.45% | 2m 14s | 2 |

Accuracy is computed by `evaluate_retrieval_predictions.py` as:

```text
number of predictions whose executed row multiset equals the expected row multiset
----------------------------------------------------------------------------------
                              number of predictions
```

This is a strict and appropriate primary metric for the task. 

### New answerability metric

| Framework | Non-abstained | Abstentions | Total | Answerability rate |
|---|---:|---:|---:|---:|
| RTF | 111 | 44 | 155 | 71.61% |
| RACE | 152 | 3 | 155 | 98.06% |
| ICIO | 119 | 36 | 155 | 76.77% |

The metric implemented in `metric_implementation.py` is:

```text
number of predictions other than SELECT NULL;
------------------------------------------------ × 100
                 total predictions
```

It measures the model's willingness to produce a query, not whether that query is
valid or correct. Therefore, answerability rate complements execution accuracy and
must not replace it.

## Graphs

### Execution accuracy

```text
Scale: each █ is approximately 2 percentage points

RTF   21.94% | ███████████
RACE  27.74% | ██████████████
ICIO  26.45% | █████████████
```

### Answerability rate

```text
Scale: each █ is approximately 2 percentage points

RTF   71.61% | ████████████████████████████████████
RACE  98.06% | █████████████████████████████████████████████████
ICIO  76.77% | ██████████████████████████████████████
```

### Runtime

```text
Scale: each █ is approximately 5 seconds

RACE  56s  | ███████████
RTF   89s  | ██████████████████
ICIO 134s  | ███████████████████████████
```

The runtime graph should be interpreted as an operational observation rather than a
property of the prompt framework alone. File handling, model-service load, output
length, and retry behavior can also affect elapsed time.

## Pairwise comparisons

### Accuracy

| Comparison | Difference in accuracy | Difference in correct predictions | Interpretation |
|---|---:|---:|---|
| RACE − RTF | +5.80 percentage points | +9 | Meaningful observed advantage, but not statistically significant from aggregates |
| ICIO − RTF | +4.51 percentage points | +7 | Moderate observed advantage, but not statistically significant from aggregates |
| RACE − ICIO | +1.29 percentage points | +2 | Very small observed difference |

Using an approximate two-sided two-proportion z-test on the aggregate counts gives
the following p-values:

| Comparison | Approximate p-value | Conclusion at α = 0.05 |
|---|---:|---|
| RACE vs RTF | 0.24 | Not significant |
| ICIO vs RTF | 0.35 | Not significant |
| RACE vs ICIO | 0.80 | Not significant |

These results do **not** establish that the frameworks have equal quality. They
indicate that 155 examples are insufficient to distinguish the observed accuracy
gaps reliably using only the aggregate counts. The observations are also paired by
question, so the ideal test would compare each framework's success/failure on the
same question using McNemar's test. The required discordant-pair counts are not
reported by the existing scripts.

### Answerability

| Comparison | Difference in answerability | Difference in predictions | Approximate p-value | Conclusion |
|---|---:|---:|---:|---|
| RACE − RTF | +26.45 percentage points | +41 answered | <0.001 | Statistically significant |
| RACE − ICIO | +21.29 percentage points | +33 answered | <0.001 | Statistically significant |
| ICIO − RTF | +5.16 percentage points | +8 answered | 0.30 | Not significant |

The significance of RACE's answerability advantage is much clearer than any
accuracy advantage. This distinction is central: RACE answered many more questions,
but most of those additional attempts did not translate into exact-result
correctness.

## Interpretation of the frameworks

### RTF

RTF gives the model a strong role, a step-by-step task definition, a strict output
format, and an explicit abstention policy. The explicit instruction to abstain when
the schema is insufficient likely explains its 44 abstentions and lowest
answerability rate. This conservatism can be useful when false or invented SQL is
more costly than refusing to answer.

However, the lower accuracy shows that conservatism alone did not produce the best
results. Some questions that could have been answered may have been classified as
uncertain, and the prompt does not provide worked examples to resolve recurring
SQL-generation patterns.

### RACE

RACE has the highest answerability and accuracy and is the fastest framework. Its
`Action`, `Context`, and `Expectation` sections clearly state the required file,
schema, output columns, row-order constraint, and fallback query. Compared with RTF,
it is less restrictive in tone: it states what to generate and when to use
`SELECT NULL`, but does not repeat the role's “never” constraints as extensively.

The result suggests that RACE produced a better balance between following the
required file format and attempting difficult questions. Its high answerability is
also a warning: it may guess on questions where abstention would be safer. The
primary accuracy metric prevents that behavior from being mistaken for success.

### ICIO

ICIO explicitly labels the instruction, context, input, and output and includes two
concrete output examples. The examples demonstrate capitalization, aliases,
filtering, ordering, `LIMIT`, and the abstention form. This likely helps the model
understand the desired output shape and explains why ICIO is close to RACE in
accuracy.

ICIO nevertheless abstained on 36 questions and was the slowest framework. Its
longer prompt and example material may increase processing time. However, more explicit
format guidance did not produce a measurable accuracy advantage over RACE.

## Factors: prompt, model, and coding agent

The experiment changes the **prompt framework** while keeping the task, dataset,
schema, and intended output format constant. The model and coding agent are
the same across the three sessions, so they are controlled factors in this
comparison rather than independently measured treatments.

| Factor | Role in this experiment | What can be concluded |
|---|---|---|
| Prompt framework | Independent variable: RTF, RACE, or ICIO | The observed differences are compatible with prompt structure affecting abstention, formatting, and SQL-generation behavior |
| Model | Held constant | Its absolute capability affects all scores, but this experiment cannot compare models |
| Coding agent | Held constant | It may affect file discovery, CSV handling, retries, and execution time, but its independent effect cannot be estimated |
| Dataset/schema | Held constant | The conclusions apply to this 155-question restaurant task; generalization is not established |

Because model and agent were not varied factorially, it would be incorrect to claim
that RACE is universally superior or that the coding agent caused a particular
difference. A stronger follow-up would run every prompt with several models and
several agent configurations, repeat each condition, and analyze prompt × model and
prompt × agent interactions.

## Conclusion

RACE is the strongest practical choice for this experiment: it was fastest, produced
the most exact-result-correct queries, and almost never abstained. Its accuracy
advantage over RTF and ICIO is modest and not statistically significant from the
available aggregate results, whereas its answerability advantage is large and
statistically significant. Consequently, the evidence supports the claim that RACE
encouraged more attempts, but does not prove a robust improvement in SQL correctness.

The safest final assessment is therefore: **RACE is the best observed prompt for
this dataset, while execution accuracy remains the decisive quality metric and
answerability is a useful complementary diagnostic.**
