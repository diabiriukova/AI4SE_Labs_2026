# Results
- RTF:
Time: 1m 29s
Accuracy: 0.2194 (21.94%)
Correct: 34/155

- RACE:
Time: 56s
Accuracy: 0.2774 (27.74%)
Correct: 43/155

- ICIO:
Time: 2m 14s
Accuracy: 0.2645 (26.45%)
Correct: 41/155

# Analysis
- RTF — Role, Task, Format
RTF achieved the lowest accuracy, with 34 correct queries out of 155 (21.94%). It completed the task in 89 seconds. Although its execution time was moderate, it produced nine fewer correct queries than RACE.

- RACE — Role, Action, Context, Expectation
RACE performed best, achieving 43 correct queries (27.74%) in just 56 seconds. Compared with RTF, it produced nine additional correct queries and improved accuracy by 5.80 percentage points. It was also 33 seconds faster, reducing execution time by approximately 37%.
Compared with ICIO, RACE produced two additional correct queries and completed the task 78 seconds faster.

- ICIO — Instruction, Context, Input, Output
ICIO achieved the second-highest accuracy, with 41 correct queries (26.45%). However, it took 134 seconds, making it the slowest method. Its accuracy was only 1.29 percentage points below RACE, but it required approximately 2.4 times as long to finish.

# Conclusion
The results show that RACE achieved the highest accuracy and the shortest execution time.