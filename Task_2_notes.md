# Task 2 ADR discussion notes

## Initial review of Task 1

Task 1 compared:

1. A service-oriented layered application/modular monolith with shared relational storage and typed module boundaries.
2. Independently deployable microservices with service-owned data, network APIs, broker events, and saga-based checkout.
3. An event-driven serverless workflow using managed identity, functions, queues, event buses, and durable workflows.

The prior discussion established these decisions and assumptions:

- Small team with limited deployment, monitoring, and troubleshooting capacity.
- Payment and shipment are CDC business responsibilities, while execution may use external providers.
- CDC must not store card details directly.
- Merchants have privileged product-management permissions enforced server-side.
- Orders snapshot product name, unit price, and quantity at checkout.
- Local order/price operations need strong consistency; payment/shipment updates may be asynchronous.
- Payment uncertainty is owned by Payment, resolved through reconciliation and stable idempotency keys.
- A paid order remains paid if shipment creation is delayed.
- The meaning of “distributed system” remains unresolved.

## Initial ADR created

Created `architecture_decision_record.md` with status **Proposed** and ADR number **ADR-001**.

The initial decision is conditional:

- Use the modular monolith as the provisional baseline because it best fits the small-team and strong-local-consistency assumptions.
- Do not claim that it satisfies independently deployable internal distribution.
- Switch the decision toward microservices if internal independent deployment is a confirmed requirement.
- Treat serverless as workload- and cloud-strategy-dependent rather than the default.

The ADR includes:

- Context and confirmed versus assumed requirements.
- All three options and a compact comparison table.
- Component ownership for Identity/Profile, Catalog, Cart, Order, Payment, Shipping, Contact, and API/BFF.
- Browse, checkout, payment-timeout, shipment-delay, and tracking flows.
- A Mermaid diagram matching the modular-monolith baseline.
- Security, consistency, payment, shipment, testing, and operational implications.
- Open questions and conditions for reconsideration.

## Review history

### Initial ADR review feedback

The user assessed the initial ADR as mostly good but requested targeted changes:

- State which architecture was chosen and why, rather than only conditionally describing the alternatives.
- Add security and identification details.
- Confirm that the Mermaid diagram is consistent with the decision and explain that consistency.

### Revision 1 changes

- Made the modular monolith the explicit provisional choice for the current assumptions.
- Explained why microservices and serverless were rejected for now.
- Clarified that the choice does not satisfy a confirmed strict internal-independent-deployment requirement; that requirement would trigger a new decision in favor of microservices.
- Added a dedicated Security and identity section covering credential ownership, authentication, server-side authorization, customer/merchant access, password hashing, transport security, provider secrets, webhook verification, rate limiting, and auditing.
- Expanded the diagram explanation to distinguish the one deployable application from its networked payment/carrier integrations.

The ADR is now ready for a second review. At least one further revision remains required.

### Revision 1 review feedback

The user found Revision 1 ready with only minor wording changes, but requested a final quality pass to:

- Check missing consequences, unclear ownership, unsupported assumptions, and payment/shipment failure handling.
- Remove repeated trade-off explanations and excessive implementation detail.
- Avoid unsupported performance claims.

### Revision 2 changes

- Replaced the ownership bullet list with a compact component responsibility table.
- Added explicit payment outcomes for confirmed failure versus unknown outcome.
- Added the consequence and handling of prolonged shipment failure, while leaving refund/cancellation/manual intervention as an open business rule rather than inventing one.
- Added the shared failure-domain and support/recovery consequences.
- Marked provider idempotency/webhook capabilities as assumptions rather than confirmed facts.
- Reduced repetition while preserving the rationale, security controls, comparison, and reconsideration conditions.

Revision 2 is ready for final review. The ADR should only be called final after the user confirms that no further changes are needed.

### Final review feedback

The user requested one final targeted revision. Required changes were:

- Correct and validate the Mermaid diagram so it visibly represents one deployable application, distinguishes internal calls from external network calls, and does not imply independent deployment of every module.
- Clarify that module ownership means logically separated tables/repositories in one database deployment, with defined interfaces instead of unrestricted direct table access.
- Make checkout/payment ordering explicit: the order is not `PAID` before confirmed success, and a crash after provider success is recovered through durable state and reconciliation.
- Explain durable outbox/retry processing across application restarts; do not rely on an in-memory background job.
- Present microservices/serverless trade-offs as platform- and implementation-dependent rather than absolute.
- Remove repetition and keep confirmed requirements, assumptions, and the unresolved distributed-system interpretation distinct.

### Final revision changes

- Rewrote Option 1 and the decision to distinguish one database deployment from logical module ownership.
- Added the durable outbox/retry sequence and crash-recovery behavior.
- Clarified pending, unknown, confirmed failure, and confirmed success payment states.
- Replaced the Mermaid diagram with a `CDC Shop application - one deployable unit` subgraph, one relational database deployment, solid internal module edges, and dashed external provider/carrier calls and callbacks.
- Adjusted comparison wording to make operational burden and portability dependent on implementation/platform choices.
- Condensed implementation/security implications without removing key safeguards.

The final ADR preserves the unresolved question: it does not claim that the modular monolith satisfies a strict requirement for independently deployable internal services.
