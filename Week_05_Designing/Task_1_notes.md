# CDC Shop architectural analysis

## Requirements from `Week_05_Designing/Tasks/data/CDC.txt`

### System purpose

CDC Shop is described as a distributed system for managing products sold by a hardware store, accepting customer payments, and handling shipment/package information.

### Functional requirements

- **Customer identity and profile:** register, log in, view profile, and log out.
- **Product discovery:** view the product list, view product details, search by name, and sort by ascending or descending price.
- **Cart and purchase:** view the current cart, add products, remove all cart items, and pay for the current cart.
- **Orders and shipment:** inspect an order and see information about its package.
- **Merchant administration:** log in to the merchant area, view the merchant profile, log out, browse/search/sort products, change product prices, and insert or remove products.
- **Static and communication features:** access the About Us page and contact the shop with questions.

The stories mention two roles: **Customer** and **Merchant**. The requirements do not describe role permissions beyond the operations implied by those stories.

### Non-functional requirements explicitly stated

- The system is distributed.
- It handles management, payment, and shipment.

### Non-functional requirements that are important but unspecified

The file does not define availability, latency, throughput, scalability, consistency, recovery objectives, auditability, accessibility, localization, observability, or compliance requirements. Payment and personal data imply that security, privacy, secure credential storage, authorization, encrypted communication, and payment-provider compliance are important assumptions, but their exact targets are not given.

### Constraints and missing information

- No technology, hosting, database, deployment, or integration constraints are specified.
- The payment provider and shipment/carrier system are unspecified. It is unclear whether payment and shipping are internal services or external integrations.
- Product fields are unspecified: identifier, description, images, stock, categories, price currency, tax, and availability are unknown.
- Cart semantics are unspecified: quantity, price snapshot, persistence, expiration, and behavior when a product is removed or repriced.
- Order lifecycle and package states are unspecified, as are shipping addresses, delivery estimates, tracking numbers, and refunds/cancellations.
- Registration/profile fields, password-reset behavior, session expiration, and identity verification are unspecified.
- It is unclear whether merchants have multiple accounts, permissions, or approval workflows.
- The contact feature has no channel or workflow specified (form, email, ticket, and response tracking are all possible).
- The wording “order the products” is interpreted as **sort products**, not place an order, because it appears beside search and list stories.
- Concurrency rules are needed for simultaneous merchant updates and purchases, especially stock and price changes.

## Architecture 1: service-oriented layered application

### High-level structure and rationale

Use one deployable application composed of explicit business modules, exposed through an API and a web/mobile client. The application is internally modular but uses a shared relational database. Payment and shipping are integration boundaries, represented by dedicated adapters. This is a pragmatic first architecture: it respects the distributed-system context at the client/integration boundaries without introducing the operational cost of independently deployed microservices before scale requirements are known.

```text
Customer UI / Merchant UI
          |
      API gateway
          |
  Auth | Catalog | Cart | Order
  Profile | Contact | Merchant modules
          |
   Application/domain services
          |
     Relational database
       /            \
 Payment adapter   Shipping adapter
       |                |
 external provider   carrier/fulfilment system
```

### Components and communication

- **API gateway/BFF:** HTTPS termination, request authentication, rate limiting, and role-aware routing. A single BFF can shape responses for customer and merchant screens.
- **Identity and profile module:** registration, password hashing, login/session or token issuance, profile reads, and logout/revocation.
- **Catalog module:** product CRUD for merchants; validated list, name search, price sorting, and detail reads for both roles.
- **Cart module:** customer cart ownership, item quantities, and add/view/clear operations.
- **Order module:** validates a cart, creates an order, stores immutable line-item price snapshots, and exposes order/package status.
- **Payment adapter:** isolates provider-specific APIs and maps provider outcomes to internal payment states.
- **Shipping adapter:** creates shipment requests and maps carrier/warehouse updates to package status.
- **Contact module:** validates customer messages and sends them to a configured support channel or stores them as tickets.
- Modules communicate through typed in-process application interfaces. External payment/shipping calls use HTTPS APIs and timeouts; webhooks must be authenticated and idempotent.

### Data and operation flows

All business data is stored in normalized relational tables such as users/roles, products, carts/cart_items, orders/order_items, payments, shipments, and contact_messages. Repositories hide SQL access; application services enforce authorization and validation.

**Browse:** client requests catalog filters; the catalog service validates sort/search parameters and uses indexed product name/price queries.

**Add and pay:** the cart service verifies the customer and product availability, then updates the cart transactionally. Checkout re-reads current product data, creates an order with price snapshots, and creates a pending payment record in one local transaction. The payment adapter then calls the provider. A verified callback or reconciliation job transitions payment state. Shipment creation occurs only after the configured successful-payment rule.

**Merchant price/product update:** authorization checks the merchant role, validates fields and invariants, and commits the change with optimistic locking/version checks. Existing order lines remain unchanged because they contain snapshots.

**Package tracking:** the shipping adapter submits a shipment and stores an external ID. Authenticated carrier callbacks update a shipment state machine; customers read the resulting status through the order module.

### Candidate technologies and patterns

- REST/JSON or GraphQL API; HTTPS and an API gateway/reverse proxy.
- A typed service framework (for example Spring Boot, ASP.NET Core, NestJS, or FastAPI) with a relational database such as PostgreSQL.
- Repository/unit-of-work pattern, DTO validation, RBAC, optimistic concurrency, and an outbox table for reliable external-event publication.
- Redis is optional for sessions, rate limits, or read caching, but the relational database remains the source of truth.
- Provider SDKs are wrapped behind ports/adapters; a test payment/shipping adapter supports automated tests.

### Benefits and disadvantages

**Benefits:** low deployment and operational complexity; straightforward transactions across cart/order/payment records; consistent authorization and validation; easy local development and end-to-end testing; clear module boundaries leave a migration path to services.

**Disadvantages:** modules share a process and database, so failures and load are less isolated; catalog traffic can compete with checkout; independent scaling and team ownership are limited; a defect or deployment can affect the whole application.

### Key trade-offs and painful implementation details

- **Consistency vs. external reality:** a database transaction cannot include a remote payment or carrier call. Use explicit pending/failed states, idempotency keys, timeouts, retries with limits, webhook verification, and reconciliation rather than pretending the operation is atomic.
- **Checkout concurrency:** lock or version-check cart/product rows, define stock behavior, and ensure repeated checkout requests cannot create duplicate charges/orders.
- **Security:** hash passwords with a modern password KDF, never store card data, enforce server-side RBAC, validate ownership of carts/orders, protect webhooks, and audit merchant changes.
- **Errors:** return stable problem responses; distinguish validation, authentication, authorization, unavailable-provider, and conflict errors. Do not silently treat payment uncertainty as success.
- **Migrations/deployment:** use versioned backward-compatible migrations, health checks, secrets management, database backups, and structured logs/correlation IDs.
- **Testing:** unit-test domain rules; integration-test transactions and repositories; contract-test payment/shipping adapters; use end-to-end tests for registration, cart, checkout, merchant updates, and shipment callbacks.

### When this is a good or bad choice

It is a good default for a small or medium shop, an academic project, or a team that needs reliable transactional behavior and fast delivery without evidence for independent scaling. It is a poorer choice if catalog, checkout, payment, or shipping must be deployed and scaled independently, if teams require strict ownership boundaries, or if the system must tolerate broad process/database failures through strong service isolation.

## Discussion record

### User clarification and question

- The user considers a single deployable application with well-defined internal modules an acceptable first design because it supports maintainability, testing, transactions, and shared-database consistency.
- Payment processing and shipment management are CDC business responsibilities. Actual payment execution and physical delivery may be delegated to external providers, but the choice of provider is an assumption rather than a confirmed requirement.
- If payment succeeds and the application crashes before shipment creation, the paid order remains recorded and shipment creation is retried after recovery. Retries must be idempotent so the customer is not charged again.
- The user asked how to divide modules, assign data ownership, and avoid tight coupling.

### Module boundaries and data ownership

The modules share one database deployment for operational simplicity, but they do **not** share unrestricted table access. Each module has an owning service/repository layer; other modules use a typed application interface or an integration event rather than modifying the owner's rows directly.

| Module | Owns | Responsibilities | Allowed interactions |
|---|---|---|---|
| Identity and Profile | `users`, credentials, roles, profile data, sessions/revocations | Register, authenticate, logout, profile reads, password/security rules | API gateway asks it to authenticate/authorize; other modules receive a user ID and role, not password data |
| Catalog | `products`, product versions, catalog status | Customer/merchant listing, name search, sorting, details, merchant price and product CRUD | Cart and order request product snapshots/availability through a catalog interface; they do not update product rows |
| Cart | `carts`, `cart_items` | Add, view, quantity changes if supported, clear, ownership checks | Uses catalog read interface to validate product references; checkout asks it for a validated cart and then marks/clears it through its interface |
| Order | `orders`, `order_items`, order status/state history | Turn a cart into an order, preserve immutable price/description snapshots, expose customer order views | Reads a cart through Cart API; requests payment through Payment API; requests shipment through Shipping API; owns order status transitions |
| Payment | payment records, provider references, idempotency keys, payment state history | Start/confirm/refund payment, process verified callbacks, reconcile uncertain provider states | Order sends a payment command; Payment calls the provider adapter; Payment reports state changes without exposing provider secrets |
| Shipping | shipments, package/tracking state history, carrier references, shipment idempotency keys | Create shipment after the payment rule is satisfied, process carrier callbacks, expose package information | Order sends a shipment command; Shipping calls carrier adapter; customers read shipment information through Order/Shipping query APIs |
| Contact | contact messages/tickets and delivery status | Validate customer questions and route/store them | Uses a mail/helpdesk adapter or internal support queue; it does not modify profile or order data |
| API/BFF | no business-owned data | Maps client requests to module interfaces, authentication context, response DTOs, rate limits | Must not contain business rules or write module tables directly |

For example, a merchant price change calls `Catalog.changePrice(productId, newPrice, expectedVersion)`. Cart does not update `products` itself. During checkout, Order asks Cart for a checkout representation and asks Catalog for a current validation/snapshot; Order then stores its own immutable line-item values. A later catalog price change therefore cannot rewrite an existing order.

### Communication without tight coupling

- Prefer small, stable command/query interfaces such as `getProductForCart`, `createOrderFromCart`, `authorizePayment`, and `createShipmentForPaidOrder`; pass DTOs rather than ORM entities or database connections.
- Keep each module's domain model private. Public interfaces expose identifiers, validated values, and explicit error types, not internal tables.
- Use domain events for facts that do not require an immediate response, for example `PaymentSucceeded` or `OrderPaid`. An outbox record is committed with the state change and a worker delivers it, preventing a crash between database commit and message publication.
- Use correlation IDs in every request/event and idempotency keys for checkout, payment, and shipment commands. A repeated `createShipmentForPaidOrder(orderId)` returns the existing shipment instead of creating a second one.
- A shared database is an implementation constraint, not a reason to use cross-module SQL joins. Cross-module reporting can use read models or explicit query services; if performance later requires it, a module can be extracted behind the same interface.

For the payment-recovery case, Payment records a provider reference and idempotency key before/while calling the provider, and Order records `PAID` only from a confirmed provider result. Shipping consumes the paid-order fact or a durable retry job. If shipment creation fails, it retries with the same order/shipment idempotency key; no new payment attempt is made.

### User conclusion about boundaries

- Catalog owns the current product price, while Order determines and persists the immutable price used at checkout.
- Payment and its provider adapter own payment uncertainty and reconciliation.
- Payment retries use a stable idempotency key tied to the checkout/order attempt.
- For a modular monolith, the user prefers clear business responsibilities over making every function a separate module.

This supports keeping a small number of cohesive modules rather than splitting every operation into a service. Architecture 1 is provisionally accepted as a pragmatic baseline; the next discussion should compare it with a genuinely independently deployable microservices design.

The user wants to compare all three architectures before selecting one because the system is required to be distributed. No priority between simplicity and failure isolation has been selected yet.

The architecture discussion should now validate:

1. Whether one deployable application is acceptable despite the system being called distributed.
2. Whether payment and shipping are external systems and what consistency guarantees are expected.
3. Whether product stock, quantities, addresses, refunds, and shipment tracking are in scope.
4. Which security, availability, and scale assumptions should constrain the architecture.

## Comparison and unresolved items

Architecture 2 is introduced below; Architecture 3 and the final comparison will be added after it is challenged and clarified.

## Architecture 2: independently deployable microservices

### High-level structure and rationale

Split the business capabilities into independently deployable services, each owning its data. This directly interprets “distributed system” as a set of networked components and allows catalog traffic, checkout, payment, and shipment workflows to scale or fail independently.

```text
Customer UI / Merchant UI
          |
      API gateway
   /       |        \
Identity  Catalog   Cart
   |         |        |
 own DB    own DB   own DB
          |
       Order service ---- message broker ---- Payment service
          |                                      |
       own DB                              payment provider
          |
     Shipping service ---------------------- carrier
       own DB
```

### Services and responsibilities

- **Identity service:** accounts, credentials, roles, sessions/tokens, and profile data. Other services receive a user identity/role claim and do not read identity tables.
- **Catalog service:** product CRUD, current prices, search/sort queries, and product availability. It owns the product database and publishes product-change events.
- **Cart service:** customer cart and items. It asks Catalog for product validation or consumes a catalog read model; it owns cart persistence.
- **Order service:** order state machine, immutable line-item snapshots, addresses/order history, and the customer-facing order view. It coordinates checkout through commands/events but cannot transactionally update Cart, Payment, or Shipping databases.
- **Payment service:** payment attempts, provider references, idempotency keys, payment state, verified callbacks, refunds, and reconciliation. It alone calls the payment provider.
- **Shipping service:** shipment records, carrier references, package states, retries, and verified carrier callbacks. It alone calls the carrier.
- **Contact service:** customer questions and support delivery/ticket integration.
- **API gateway and broker:** authentication enforcement/routing and asynchronous delivery. The gateway is not a business-data owner; the broker is not the source of truth.

### Data, communication, and operation flows

Each service owns a separate schema/database. Synchronous REST/gRPC calls are appropriate for short queries and commands needing an immediate answer; domain events over a broker are appropriate for facts and long-running workflows. No service performs cross-database joins or writes another service's tables.

**Browse:** the gateway routes to Catalog. Search indexes (for example PostgreSQL indexes or OpenSearch) support name search and price sorting. Merchant updates commit in Catalog and publish `ProductChanged`; optional read models refresh asynchronously.

**Checkout:** Order requests a cart representation from Cart and current product validation from Catalog. It writes an order with snapshots, then emits `OrderCreated` or `PaymentRequested`. Payment creates an attempt with a stable idempotency key and calls the provider. A confirmed result emits `PaymentSucceeded`; Order marks the order paid and emits `ShipmentRequested`; Shipping creates the shipment and retries with the same shipment key until accepted. This is a saga, not one distributed database transaction.

### Technology and patterns

- REST or gRPC for synchronous service APIs; Kafka, RabbitMQ, NATS, or a cloud queue for events.
- PostgreSQL per service where relational transactions matter; Redis for short-lived cart/session data; OpenSearch only if search scale requires it.
- Saga/process manager for checkout, outbox/inbox tables for reliable event publication and deduplication, schema/versioned events, circuit breakers, timeouts, and dead-letter queues.
- Containerized deployment with Kubernetes or a managed container platform; centralized logs, traces, metrics, and secrets management.

### Benefits, disadvantages, and implementation pain

**Benefits:** independent scaling and deployment; stronger fault boundaries; separate data ownership; teams can evolve Catalog, Payment, and Shipping independently; provider failures can be isolated and retried.

**Disadvantages:** high operational and cognitive complexity; network failures and eventual consistency become normal; local development and end-to-end testing are harder; duplicated DTOs/read models and API/event versioning add maintenance cost.

The difficult details include distributed tracing, authentication propagation, event ordering and deduplication, schema evolution, saga compensation (for example refunding a payment if an order cannot be fulfilled), stale catalog/cart data, and deciding what the customer sees while a workflow is pending. A provider timeout must not be interpreted as failure without reconciliation. A unique payment idempotency key and provider reference prevent duplicate charges. Database-per-service improves ownership but makes reporting and cross-service queries require APIs or projections.

### Good and bad fit

This is a good choice if the assignment or expected future scale requires independently deployable distributed components, distinct team ownership, or strong isolation around payment/shipping. It is a poor choice for a small team or simple deployment where the operational burden outweighs independent scaling, or where immediate cross-module consistency is more valuable than service isolation.

### Discussion record for Architecture 2

- For an uncertain provider response, the customer should see that payment is being confirmed and should not retry. Payment owns an `UNKNOWN`/`PENDING_CONFIRMATION` attempt, reconciles by provider query or webhook, and reuses the same idempotency key.
- After confirmed payment but unavailable Shipping, the customer should see that payment succeeded while shipment preparation is delayed. The paid order remains recorded and Shipping retries; Payment does not charge again.
- The user will assess whether microservices are justified after seeing Architecture 3.
- The user asked about Contact service and identifying services. Contact is a separate service only if contact messages need their own persistence, moderation, support workflow, delivery retries, or independent scaling. For a small system it can instead be a module in the application or a function that sends/stores a message. Identity should remain a shared platform boundary: it owns credentials, sessions/tokens, and roles; Profile data may stay with Identity or be a separate Profile service only if profile lifecycle/scale/team ownership warrants it. Business services consume a verified subject/role claim and never access credential storage.

## Architecture 3: event-driven serverless workflow

### High-level structure and rationale

Use managed identity, API endpoints, serverless functions, managed databases, and an event bus/queue. Synchronous APIs handle short user interactions; durable events and workflow functions handle payment confirmation, shipment creation, retries, and contact delivery. This is genuinely different from both a shared-process modular monolith and long-running independently deployed microservices: deployment units are small functions and managed workflow steps, and the platform supplies much of the scaling and availability.

```text
Web client
    |
API gateway + managed identity
    |
Functions: Catalog | Cart | Checkout | Merchant | Contact
    |                 |
managed DBs/read     Event bus / durable workflow
models                |          |           |
                 Payment fn   Order fn    Shipping fn
                      |           |           |
                payment API  order store  carrier API
```

### Components and communication

- **Managed identity:** registration, login, token issuance, and role claims.
- **Catalog and merchant functions:** validate product CRUD, publish catalog-change events, and serve indexed reads from a managed database/search service.
- **Cart functions:** handle customer cart commands and persist cart state.
- **Checkout/order workflow:** a durable state machine coordinates cart validation, order creation, payment confirmation, and shipment request. It stores checkpoints and resumes after function/platform failures.
- **Payment function:** owns provider calls, idempotency keys, webhook handling, and reconciliation. Secrets remain in a managed secret store.
- **Shipping function:** owns carrier calls, tracking callbacks, retry policy, and package state.
- **Contact function:** writes a message to a managed queue or ticket store and invokes an email/helpdesk adapter.
- **Event bus/queues:** decouple producers and consumers; dead-letter queues retain messages that need operator attention. Managed databases are still the source of truth for each stateful capability.

### Data and operation flows

Customer browse/search calls Catalog functions and a managed search index. Add-to-cart invokes Cart and may use a cached Catalog projection. Checkout starts a durable workflow with a client idempotency key. The workflow creates an order snapshot, starts Payment, waits for a verified success/failure/unknown result, and then requests Shipping. Each function writes its own state before acknowledging an event. Replayed events are safe because consumers use inbox records or conditional writes keyed by event ID.

For a payment timeout, the workflow enters `PAYMENT_CONFIRMATION_PENDING`; a webhook or scheduled reconciliation resumes it. For a shipping outage, it keeps `PAID` and schedules a retry with a stable shipment key. The customer reads a query projection that may be briefly eventually consistent, so the UI must show pending states rather than claim immediate completion.

### Technologies and patterns

Possible technologies include AWS Lambda + API Gateway + Step Functions + EventBridge/SQS + DynamoDB/RDS, Azure Functions + Durable Functions + Service Bus, or Google Cloud Functions/Cloud Run + Workflows + Pub/Sub. Use managed identity, secret storage, tracing, schema-versioned events, conditional writes, TTLs for carts/sessions, and infrastructure as code.

### Benefits, disadvantages, and implementation pain

**Benefits:** automatic scaling for uneven catalog/contact traffic; durable workflow resumption; reduced server administration; natural asynchronous handling of payment/shipping; pay-per-use potential; isolated function failures.

**Disadvantages:** platform coupling and potentially difficult local development; cold starts and execution/time limits; eventual consistency; distributed debugging; more complicated authorization and transaction boundaries; costs can be unpredictable at high volume; managed-service outages remain a risk.

Painful details include function retry semantics (at-least-once delivery), duplicate events, poison messages, workflow versioning, partial updates, provider webhook authentication, search-index lag, observability across short-lived functions, and safe schema migrations for managed stores. A function must never acknowledge an event before its state and retry metadata are durable. Long-running provider reconciliation belongs in a durable workflow or scheduled job, not an ordinary request function.

### Good and bad fit

This is a good choice for bursty traffic, a small operations team, and workflows that naturally consist of durable asynchronous steps. It is a poorer choice if the course/team needs portable deployment, predictable low-latency behavior, simple local debugging, or a straightforward relational transaction model. It can also be excessive if CDC has modest traffic and no operational need for elastic managed infrastructure.

### Discussion record for Architecture 3

- The user selected the Order workflow/state store, exposed through a query projection, as the source of truth for a refreshed order page.
- While the provider callback is delayed, the customer should see `PAYMENT_CONFIRMATION_PENDING` and should not retry.
- The user wants a final comparison before deciding whether serverless is appropriate.

If Order is already `PAID` but the shipping event has not been processed, the customer should see **payment successful / order confirmed / shipment preparation pending** (or an equivalent `PAID_AWAITING_SHIPMENT` status). The UI should not claim that the package has shipped. A durable event/outbox plus workflow retry eventually asks Shipping to create the shipment; the Order projection can expose a `shipmentStatus=PENDING` and the latest known update time. Payment is not repeated.

#### Serverless execution and operations

- **Potentially long-running work:** waiting for provider reconciliation, human/support approval, carrier polling, large imports, image processing, or repeated retries should use a durable workflow, queue consumer, or scheduled job rather than one request function. Each function invocation should be bounded and resumable.
- **Cold starts:** an idle function may add startup latency. Keep handlers small, choose an appropriate runtime, use provisioned/warmed capacity only for latency-sensitive paths, and do not assume every request is cold or warm.
- **Concurrency limits:** a traffic burst can exhaust account/function concurrency and cause throttling. Configure reserved/concurrent capacity, queue bursts, backpressure, and graceful retry behavior.
- **Provider quotas:** payment/carrier APIs and cloud services may impose request-rate or daily limits. Use bounded exponential backoff, provider-aware rate limiting, and reconciliation rather than uncontrolled retries.
- **Local testing:** emulate queues/workflows or use contract/integration tests against test providers; unit-test handlers and state transitions separately. Full cloud behavior, IAM, retries, and observability still require an environment-level test.
- **Cost and simplicity:** serverless may be cheaper for low or bursty traffic because idle servers are avoided, but less predictable at sustained traffic once invocation, workflow, database, queue, logging, and egress costs accumulate. A modular monolith is usually simpler and can be cheaper for modest steady workloads. The decision depends on traffic shape/volume, latency targets, operations expertise, cloud budget, portability requirements, and provider lock-in tolerance.

#### Dead-letter queues

A dead-letter queue (DLQ) is a holding queue for messages that failed processing after a configured number of attempts. Instead of retrying forever and blocking healthy work, the message is moved to the DLQ with its error and metadata. Operators or a repair process inspect it, fix the cause, and deliberately replay or discard it. A DLQ is not a silent failure path: CDC should alert on DLQ growth and preserve correlation/event IDs.

## Preliminary comparison

| Concern | 1. Service-oriented layered application | 2. Microservices | 3. Event-driven serverless |
|---|---|---|---|
| Main communication | In-process interfaces; external HTTPS | Network APIs plus broker events | API functions plus queues/workflows |
| Data consistency | Easiest local transactions; explicit external states | Saga and eventual consistency across databases | Durable workflow and eventual consistency |
| Scaling/isolation | Whole application/database boundary | Per-service deployment and scaling | Function/platform-level elastic scaling |
| Operational complexity | Lowest | Highest | High, shifted to cloud platform |
| Failure handling | Process/database failures affect broad scope | Service and network failures require resilience | Retries, DLQs, quotas, cold starts, workflow recovery |
| Testing/debugging | Simplest | Contract, integration, distributed tracing | Handler plus cloud/workflow emulation and observability |
| Portability | Relatively high | Moderate | Lowest due to managed-provider coupling |
| Best fit | Modest shop, small team, strong transaction needs | Independent team/service ownership and isolation | Bursty workload, managed operations, asynchronous workflows |
| Main risk | Shared failure/scaling boundary | Overengineering and distributed complexity | Hidden platform/cost complexity and eventual consistency |

No final architecture has been selected. The comparison still depends on workload, availability/latency targets, cloud-provider constraints, team size, and whether the distributed requirement is pedagogical or operational.

## Current conclusion

The user recommends a **conditional choice**, not one architecture yet.

### Current assumptions

- A small development team has limited time for deployment, monitoring, and troubleshooting.
- Payment processing and shipment fulfilment use external APIs; provider identity and availability guarantees are unspecified.
- Customer and merchant accounts require authentication; merchants have privileged product/price permissions; sensitive operations require server-side authorization.
- CDC does not store payment details directly; a trusted payment provider handles them.
- An order snapshots product name, unit price, and quantity at checkout; later catalog changes cannot alter past orders.
- Critical local operations, especially saving an order and its agreed price, require strong consistency.
- Payment and shipment updates may be asynchronous and temporarily inconsistent.

### Decisive unresolved question

Does “distributed system” require CDC’s internal components to be independently deployable services, or is a modular monolith that communicates with external payment and shipping providers sufficient? This answer determines whether Architecture 1 is an acceptable baseline or whether Architecture 2/3 is required by the assignment rather than merely justified by future quality attributes.

### Provisional guidance

Until that question is answered, Architecture 1 is the practical default for the small team and strong local-consistency assumptions; Architecture 2 is the clearest response if independent internal distribution is mandatory; Architecture 3 is appropriate only if managed cloud operations, asynchronous workflows, and elastic/bursty workload benefits outweigh provider coupling and debugging complexity.
