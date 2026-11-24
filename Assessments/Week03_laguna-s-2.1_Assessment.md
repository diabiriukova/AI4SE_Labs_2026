# Assessment by laguna-s-2.1

# Week 03 Prompting
- Awarded: 5b out of 5b
- Commentary: The submission is complete and well-structured across all four tasks. Three prompting frameworks (RTF, RACE, ICIO) were selected from frompting.com/frameworks, distinct from the prohibited ROSES and zero-shot approaches. Predictions were generated for all 155 dataset questions under each framework, evaluated with execution accuracy and inference timing, and a novel Answerability Rate metric was proposed, implemented, and analyzed. The final report provides comprehensive tables, visualizations, statistical significance testing, and a balanced interpretation of prompt, model, and agent factors.

## Task 1
- Awarded: 1b   (max 1b)
- Commentary: The student selected three prompting frameworks — RTF (Role-Task-Format), RACE (Role-Action-Context-Expectation), and ICIO (Instruction-Context-Input-Output) — from https://frompting.com/frameworks, correctly avoiding the prohibited ROSES and zero-shot prompting. Each framework has a fully formulated prompt in formulated_prompts.md that specifies the SQL generation task, schema usage, output file format, row-order preservation, and the SELECT NULL abstention policy. The accompanying report.md explains why each framework was chosen and what it is expected to achieve. All required outputs (prompt data file and explanatory report) are present and complete.

## Task 2
- Awarded: 1b   (max 1b)
- Commentary: Three prediction files were produced (RTF, RACE, ICIO) covering all 155 questions, with prompt identification embedded in the filenames. The report.md compares performance using execution accuracy (correct/total), inference times (89s, 56s, 134s), and per-framework analysis. The evaluation script evaluate_retrieval_predictions.py is included and executes predicted SQL against an in-memory SQLite database built from the schema and data files. The report does not itself contain an inline visualization, but the data, timing measurements, and comparative analysis are all present and the visualizations are provided in the Task 4 final report. The core deliverables of predictions-with-metadata and a comparative report with inference timing are fully satisfied.

## Task 3
- Awarded: 1b   (max 1b)
- Commentary: The student proposed the Answerability Rate (AR) — the proportion of predictions that are not abstentions (SELECT NULL;) — and defended it as a measure of the model's willingness to generate a query rather than refuse. The report explicitly argues that AR complements rather than replaces execution accuracy, correctly warning that high answerability does not imply correctness. The metric is implemented in metric_implementation.py (a working Python script that reads prediction CSVs and computes the rate). Values were calculated for all three frameworks (RTF: 71.61%, RACE: 98.06%, ICIO: 76.77%) and compared in a dedicated report. All required outputs (source code and comparison report) are present.

## Task 4
- Awarded: 2b   (max 2b)
- Commentary: The final report is thorough and well-organized. It summarizes the experimental setup, presents execution accuracy and answerability results in tables, and provides text-based bar charts for accuracy, answerability, and runtime. Statistical significance is addressed with approximate two-sided two-proportion z-tests, reporting p-values for each pairwise comparison and correctly noting which differences are significant (answerability differences are significant; accuracy differences are not, due to small sample size). The report interprets each framework's behavior, explains why the differences arise, and includes a dedicated factors table analyzing prompt framework, model, and coding agent as controlled versus varied factors. The conclusion is appropriately qualified, noting that RACE is the best observed prompt while execution accuracy remains the decisive quality metric. This fully satisfies the detailed-analysis, tables-and-graphs, significance-testing, and causal-interpretation requirements.
