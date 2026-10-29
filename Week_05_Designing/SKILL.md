---
name: architectural-decision-making
description: "Use when analyzing system requirements, comparing architectures, choosing an architecture, or creating and reviewing an Architecture Decision Record (ADR). Guides evidence-based architecture proposals, interactive trade-off discussion, decision notes, diagrams, and iterative ADR refinement."
argument-hint: "[requirements file, system description, or architecture question]"
user-invocable: true
disable-model-invocation: false
---

# Architectural decision-making

## Purpose

Use this skill to turn system requirements into an evidence-based architecture decision. It supports a requirements analysis, genuinely different architecture options, an interactive comparison, an ADR, and a concise record of decisions and uncertainties.

This is a reusable workflow. Do not copy domain-specific names, data models, or conclusions from previous projects into a new analysis.

## When to use

Invoke for requests involving:

- architecture analysis or system design;
- comparing monoliths, modular monoliths, microservices, serverless, event-driven, layered, hexagonal, or other architectures;
- selecting an architecture based on requirements and constraints;
- writing, reviewing, or revising an ADR;
- documenting architecture trade-offs, failure modes, integrations, consistency, security, or operational concerns.

Do not use as a substitute for detailed implementation, performance benchmarking, threat modeling, or infrastructure design unless the user explicitly includes those scopes.

## Required artifacts

Unless the user specifies different paths, maintain:

- `Task_1_notes.md` or an equivalent requirements/discussion record;
- `Task_2_notes.md` or an equivalent ADR review/revision record;
- `architecture_decision_record.md` or the repository's existing ADR convention.

Create notes early and update them after every substantive discussion or revision. Notes must distinguish:

- confirmed requirements;
- assumptions;
- constraints;
- open questions;
- user feedback and decisions;
- changes made and their rationale.

Never fabricate user questions, user understanding, requirements, provider capabilities, performance targets, or completed validation.

## Workflow

### 1. Inspect before proposing

1. Read the supplied requirements source thoroughly before designing.
2. Inspect relevant existing architecture notes, ADRs, repository conventions, and templates.
3. If the requirements are in a file, read only the requested scope when the user explicitly limits it.
4. Do not implement application software unless the user separately requests implementation.

Record a concise requirements inventory:

- actors and roles;
- functional capabilities and important workflows;
- explicit non-functional requirements;
- constraints and dependencies;
- security and privacy implications;
- data ownership and lifecycle clues;
- ambiguity, missing information, and contradictory statements.

### 2. Separate evidence from interpretation

Use explicit headings or tables for:

| Category | Meaning |
|---|---|
| Confirmed requirement | Directly stated or explicitly confirmed by the user |
| Assumption | A provisional interpretation needed to compare designs |
| Constraint | A boundary imposed by the project, team, technology, policy, or environment |
| Open question | Information that could materially change the decision |

Do not silently turn an assumption into a requirement. Keep unresolved architectural drivers visible, especially the meaning of words such as “distributed,” “real-time,” “secure,” or “scalable.”

### 3. Identify architectural drivers

Prioritize drivers that can change the architecture:

- workload shape, scale, latency, and growth;
- consistency, transactions, concurrency, and data ownership;
- availability, recovery, failure isolation, and acceptable degradation;
- authentication, authorization, privacy, secrets, auditability, and compliance;
- external payment, shipping, identity, messaging, or other integrations;
- team size, ownership boundaries, skills, deployment, monitoring, and operations;
- portability, cloud dependence, cost predictability, and testing needs.

Label unknown drivers as open questions instead of inventing targets.

### 4. Propose genuinely different options

Propose at least three options when the scope supports it. Options must differ in structure, deployment, data ownership, or communication model—not merely use different product names.

For each option explain:

1. structure and why it fits the drivers;
2. major components and ownership;
3. synchronous and asynchronous communication;
4. data storage, validation, transactions, and updates;
5. important operation flows;
6. technologies and alternatives as examples, not commitments;
7. benefits, disadvantages, and trade-offs;
8. failure modes and recovery;
9. security, testing, migrations, observability, and deployment implications;
10. when it is a good or bad choice.

Useful distinct families include:

- modular monolith or layered application;
- independently deployable microservices;
- event-driven/serverless workflow;
- a separately justified alternative such as a modular monolith with CQRS, a workflow-oriented architecture, or a platform-specific design.

Do not recommend microservices merely because the system is called distributed. Do not claim serverless is automatically cheaper, simpler, or more scalable.

### 5. Discuss interactively

Do not dump all options and end the conversation. Introduce one option, ask focused questions, and record the answers. Test understanding with concrete scenarios such as:

- concurrent updates to a product and checkout;
- an external provider timeout after it may have accepted a request;
- payment confirmation followed by shipping unavailability;
- a process crash between a local commit and an external call;
- a customer refreshing a page while state is pending.

Explain uncertainty plainly and revise the model when the user's answers change it. Before moving to the next option, record the option's accepted assumptions, rejected concerns, and unresolved issues.

### 6. Compare and recommend

Use a compact comparison table with criteria relevant to the system, for example:

| Criterion | Option A | Option B | Option C |
|---|---|---|---|
| Local transaction model |  |  |  |
| Independent deployment |  |  |  |
| Failure/scaling isolation |  |  |  |
| Operational complexity |  |  |  |
| Testing/debugging |  |  |  |
| Portability/cost uncertainty |  |  |  |

Choose based on confirmed drivers and explicit assumptions. State whether the recommendation is:

- final;
- provisional;
- conditional on an open question.

If a requirement could invalidate the recommendation, name it as a reconsideration condition. Never claim a modular monolith satisfies independently deployable internal services.

### 7. Create the ADR

Use the template in [adr-template.md](./references/adr-template.md) or an existing repository convention. The ADR should normally contain:

- title, number, status, and date;
- context and problem statement;
- confirmed requirements, constraints, assumptions, and open questions;
- options considered and a compact comparison;
- explicit decision and rationale;
- component ownership and important flows;
- consequences, including negative consequences;
- security and identity;
- consistency and concurrency;
- payment/shipment or other integration failure handling;
- implementation implications;
- diagram where it clarifies the decision;
- reconsideration conditions.

Keep the ADR concise. Remove repeated explanations and unsupported performance claims.

### 8. Make external operations durable and idempotent

For payment, shipping, messaging, or other non-transactional integrations:

- distinguish pending, unknown, confirmed success, and confirmed failure;
- do not treat a timeout as confirmed failure;
- use a stable idempotency key for retries;
- authenticate and verify callbacks/webhooks;
- persist provider references and retry/reconciliation state;
- use an outbox or durable retry record when a local commit must trigger an external call;
- ensure records survive process restarts;
- use bounded retries, reconciliation, and explicit operator handling for permanent failures.

Do not rely on an in-memory background task for critical processing. Do not mark an order paid before confirmed payment success. Do not invent refund, cancellation, stock, provider, or carrier behavior that the requirements do not establish.

### 9. Keep diagrams honest

Before including Mermaid or another diagram, check:

- does it show the actual deployable boundaries?
- does it distinguish internal calls from network/external calls?
- does it show data ownership accurately?
- does it imply that every module is an independently deployed service?
- do labels and arrows match the written operation flow?

For a modular monolith, place modules inside one clearly labeled deployable application and show one database deployment with logical ownership if applicable. Use different edge styles or labels for external network calls. Avoid HTML entities, decorative indentation, and syntax not supported by the target renderer.

### 10. Review and revise

After the user reviews the ADR, save each revision and update the notes with:

- feedback received;
- exact changes;
- reasons for each change;
- remaining uncertainties.

Perform at least two review/revision passes when the user asks for an interactive ADR process. Check:

- decision, table, ownership model, flows, and diagram agree;
- confirmed requirements are not mixed with assumptions;
- failure handling is technically possible;
- security claims are safeguards, not invented compliance guarantees;
- alternatives are genuinely different;
- consequences include operational and maintenance costs;
- repetition and unnecessary implementation detail have been removed.

## Validation and limitations

Validate the skill itself by checking:

1. the folder name matches the `name` frontmatter;
2. YAML frontmatter is present and valid;
3. `description` contains concrete discovery triggers;
4. referenced files exist and use relative paths;
5. the skill is under a supported project skill directory.

This static validation confirms format and discoverability prerequisites only. Do not claim the skill was loaded or tested in a new assistant session unless that actually occurred. A new session may still fail to invoke it because discovery depends on the host's skill index, synchronization, workspace trust, or model selection.

