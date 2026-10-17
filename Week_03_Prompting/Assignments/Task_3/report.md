# New Metric
The Answerability Rate (AR) — the proportion of generated SQL queries that are not abstentions (SELECT NULL;)

$$
\boxed{
\mathrm{AR} =
\frac{\#(\text{predictions} \ne \texttt{SELECT NULL;})}
{\#(\text{all predictions})}\times 100\%
}
$$

The objective was to measure how frequently each approach generated a SQL query rather than abstaining from answering.

# RESULTS

- RTF Restaurants Dataset Predictions:

Total predictions: 155

Non-abstained predictions: 111

Abstentions: 44

Answerability Rate: 71.61%

- RACE Restaurants Dataset Predictions:

Total predictions: 155

Non-abstained predictions: 152

Abstentions: 3

Answerability Rate: 98.06%

- ICIO Restaurants Dataset Predictions:

Total predictions: 155

Non-abstained predictions: 119

Abstentions: 36

Answerability Rate: 76.77%

# Analysis

The results reveal differences in the frequency with which the three approaches generated SQL queries instead of abstaining.

RACE achieved the highest answerability rate, generating SQL queries for 152 of the 155 questions (98.06%). Only three predictions were abstentions, indicating that RACE was the most likely of the three approaches to provide a SQL query for a given question.

ICIO achieved an answerability rate of 76.77%, generating 119 non-abstained predictions and abstaining on 36 questions. Its answerability rate was 5.16 percentage points higher than that of RTF.

RTF achieved the lowest answerability rate, generating SQL queries for 111 questions (71.61%) and abstaining on 44. Thus, RTF abstained more frequently than either RACE or ICIO.

The difference between RACE and RTF was 26.45 percentage points, while the difference between RACE and ICIO was 21.29 percentage points. These results suggest that RACE was substantially more willing to generate SQL queries under the evaluation conditions.

Nevertheless, a high answerability rate should not be interpreted as evidence of higher SQL correctness. An approach that generates a query for every question may achieve a 100% answerability rate while producing invalid SQL or queries that do not correctly answer the questions. Conversely, an approach that abstains more often may be more cautious when faced with questions that cannot be answered using the provided schema.

# Conclusion
The proposed metric does not replace the original metric of the problem. To obtain a more comprehensive assessment of text-to-SQL performance, future evaluation should complement answerability rate with execution accuracy, schema compliance, and semantic correctness. However, this metric establishes a comparison of the approaches in terms of their tendency to generate SQL rather than abstain.