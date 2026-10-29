# Original and skill-assisted architecture work comparison

## Title and purpose

This report compares the original CDC Shop architecture work with the revised
work produced after creating the architectural-decision-making skill. It
distinguishes directly observable evidence from judgments and does not assume
that the later work is better merely because it is later.

## Files inspected and comparison method

### Original work

- [architecture_decision_report.md](/Users/diana/matfyz/AI4SE_Labs_2026/architecture_decision_report.md)
- [Task_1_notes.md](/Users/diana/matfyz/AI4SE_Labs_2026/Task_1_notes.md)
- [Task_2_notes.md](/Users/diana/matfyz/AI4SE_Labs_2026/Task_2_notes.md)

### Revised work

- [architecture_decision_report_v2.md](/Users/diana/matfyz/AI4SE_Labs_2026/architecture_decision_report_v2.md)
- [Task_1_notes_v2.md](/Users/diana/matfyz/AI4SE_Labs_2026/Task_1_notes_v2.md)
- [Task_2_notes_v2.md](/Users/diana/matfyz/AI4SE_Labs_2026/Task_2_notes_v2.md)

### Skill guidance

- [SKILL.md](/Users/diana/matfyz/AI4SE_Labs_2026/.github/skills/architectural-decision-making/SKILL.md)
- [adr-template.md](/Users/diana/matfyz/AI4SE_Labs_2026/.github/skills/architectural-decision-making/references/adr-template.md)


The comparison uses requirements inventories, option sections, tables,
decisions, flows, diagrams, consequences, and review histories. No elapsed
time is inferred from filenames or file dates.

## Summary of the original workflow

The original Task 1 notes identify customer and merchant functionality,
payment and shipment scope, the explicit “distributed” statement, and a
substantial list of missing information including stock, cart semantics,
shipping state, refunds, identity details, provider choice, and operational
targets.

The original discussion considered three genuinely different options:

1. A modular monolith with typed internal modules and a shared relational
   database.
2. Independently deployable microservices with service-owned data and saga
   coordination.
3. An event-driven/serverless workflow with queues, functions, and durable
   workflow state.

The original ADR provisionally chooses the modular monolith for a small team
and strong local transaction needs. It explicitly preserves the unresolved
question of whether “distributed” requires independent internal deployment.
The original review rounds strengthened security, ownership, database
boundaries, payment states, durable retries, and Mermaid diagram accuracy.

## Summary of the skill-assisted workflow

The revised Task 1 notes use more explicit categories for confirmed
requirements, non-functional requirements, security implications, data
clues, and open questions. They extend the domain model with inventory
reservation and more explicit identity-provider and contact decisions.

The revised ADR, ADR-002, is marked **Accepted** and still chooses a modular
monolith with integration adapters. It adds:

- explicit Inventory ownership and reservation lifecycle;
- external identity-provider integration as a bounded decision;
- persistent authenticated carts;
- stored contact messages before optional forwarding;
- a stepwise checkout flow;
- inventory held during `PENDING`/`UNKNOWN` payment;
- a comparison table focused on transaction, recovery, isolation, and current
  evidence fit;
- a revised Mermaid diagram showing one deployable application and external
  integrations.

The skill formalizes these improvements through explicit evidence categories,
architectural drivers, interactive review, durable idempotency guidance,
diagram checks, ADR templates, and revision records.

## Comparison table

| Criterion | Original result | Revised result | Assessment |
|---|---|---|---|
| Requirements analysis | Detailed functional inventory and many missing requirements were identified in Task 1. Confirmed and unspecified items were separated by headings. | More formal inventory sections cover confirmed requirements, explicit non-functional requirements, security/privacy, data lifecycle clues, and open questions. | **Revised is easier to scan.** Original is more cautious; revised promotes inventory and identity-provider choices into bounded decisions. |
| Architecture alternatives | Three genuinely different architectures were considered fairly: modular monolith, microservices, and serverless/event-driven workflow. | The same three families are retained and described with inventory-aware flows and more explicit recovery models. | **Comparable; revised is more domain-complete.** The original already satisfied the core requirement. |
| Trade-off analysis | Discussed complexity, scalability, consistency, security, failure isolation, deployment, testing, and operations. | Adds direct trade-off wording, inventory recovery, projection staleness, replay, and platform-dependent cost/operations. | **Revised is more concise and targeted.** Original has more exploratory detail. |
| Technical accuracy | Correctly distinguished payment unknown/pending from failure, used stable idempotency and reconciliation, preserved price snapshots, and required durable outbox/retry processing. | Preserves those controls and adds reservation holding during unknown payment, explicit provider callbacks, and stepwise order/payment/inventory sequencing. | **Revised is more complete operationally.** Original is more conservative about what requirements actually confirm. |
| Architecture decision | Provisional modular-monolith decision justified by small-team assumptions and strong local transactions; strict internal distribution remains a reconsideration condition. | Accepted provisional modular-monolith decision justified by database, transaction, inventory, and evidence-fit assumptions. | **Both are justified.** Revised is more decisive, but its interpretation of “distributed” is still an assumption. |
| ADR quality | Includes context, requirements, three options, comparison, ownership, flows, security, consequences, diagram, open questions, and reconsideration conditions. | Adds a clearer evidence section, compact comparison, inventory ownership, explicit checkout flow, and accepted status. | **Revised is easier to review.** Original is stronger at visibly preserving open questions. |
| Review and iteration | Multiple rounds addressed explicit choice, security, ownership, payment/shipment failures, database semantics, durable retries, and diagram consistency. | Notes record an initial ADR, two revisions, final acceptance, diagram review, explicit trade-offs, and concision changes. | **Both are iterative.** Revised follows a more repeatable structure; original feedback is more detailed on ambiguity preservation. |
| Efficiency | Several documented discussion/revision rounds; no reliable elapsed-time evidence. | Several documented discussion/revision rounds; no reliable elapsed-time evidence. | **No measured speed improvement.** The skill improves repeatability, not demonstrably elapsed time. |

## What improved

### More consistent evidence handling

The skill explicitly requires separation of confirmed requirements,
assumptions, constraints, and open questions. This is reflected in the v2
requirements inventory and ADR sections.

### Better operational failure modeling

The revised report makes inventory reservation part of checkout and states that
an `UNKNOWN` payment holds the reservation during reconciliation. It also
keeps stable idempotency keys, verified callbacks, durable outbox/retry
records, and explicit pending/confirmed outcomes.

### More reviewable decision structure

The revised ADR has a compact comparison table, a component ownership table,
an ordered checkout flow, explicit trade-offs, consequences, and
reconsideration conditions. These correspond directly to the reusable skill
and [adr-template.md](/Users/diana/matfyz/AI4SE_Labs_2026/.github/skills/architectural-decision-making/references/adr-template.md).

### Better diagram alignment

The revised ADR explicitly labels the CDC application as one deployable unit
and uses dashed edges for external identity, payment, and carrier
integrations. This addresses the original review concern that a diagram must
not imply independently deployed modules.

## What did not improve or remains unresolved

### Meaning of “distributed”

The original work preserves this as an open question. The revised work adopts
the interpretation that external payment/shipping integration is sufficient
and says no unresolved requirement questions remain. That is a stronger
assumption than the source requirements establish. If internal independent
deployment is mandatory, both decisions must change toward microservices.

### Revised assumptions are not source requirements

The revised work treats inventory as in scope, prefers an external identity
provider, assumes authenticated persistent carts, and stores contact messages
before forwarding. These are coherent architecture decisions, but they are
not all directly stated in the original requirements. The revised ADR labels
them as decisions or bounded assumptions; they should not be reported as
confirmed source requirements.

### Original caution is lost in places

The original ADR leaves stock, quantity, address, refund, cancellation,
delivery, provider, and operational requirements visibly open. The revised ADR
closes more of these into policies. That improves completeness but risks
overcommitting if the assignment expects only requirements-supported claims.


## Conclusion

The skill made the process **more consistent, structured, and easier to
review**. Its strongest improvements are explicit evidence classification,
repeatable comparison criteria, inventory/payment recovery modeling, durable
idempotency guidance, and diagram/deployment-boundary checks.

The revised work is more concise and operationally complete in the checkout
flow, but the original work is more conservative about unresolved
requirements. There is no reliable evidence that the skill made the process
faster. Overall, the skill improved repeatability and reviewability more
clearly than it improved measured efficiency or eliminated architectural
uncertainty.
