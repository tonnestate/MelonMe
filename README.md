# MelonMe — Guerrilla Monetization MCP

**Concept v0.3.1 · October 28, 2026**  
**Status:** Concept v0.3.1 + Python MCP v0.4.0; live operation has not been verified  
**System role:** A lean, independently scoped business model connected to the existing FruitStack

> **MelonMe identifies timely purchase intent, uses relevant offers that are genuinely accessible, responds where commercial participation is permitted, and learns from actual economic outcomes. Fast, international, and designed for minimal operating costs.**
>
> **FruitStack handles reasoning and orchestration. MelonMe executes this one business model.**

## Current implementation (October 28, 2026)

The repository contains an **installable MCP v2 stdio server** exposing three executable functions: `find`, `execute`, and `learn`. The implementation is in [melonme/core.py](melonme/core.py) and [melonme/server.py](melonme/server.py). The [quickstart guide](docs/QUICKSTART.md) documents installation and inputs, while the [offline tests](tests/test_core.py) cover core behavior and error paths.

**Implemented:** Separation of buyer market and language, including cross-language search terms; a bundled HTTPS adapter for the **existing** FruitStack offer search; optional live Awin publisher-program lookups, regional promotions, and bounded searches of enhanced product feeds; Awin link creation and transaction retrieval when credentials are available; localized commercial-disclosure text in generated drafts; fallback to comparably suitable merchant offers; an optional HTTPS bridge to an existing publisher; external reply IDs as publication evidence; and commission-safe deduplication with separate aggregation of payments and costs. A failure with one partner does not halt other opportunities.

**Not demonstrated:** Availability of existing Amazon or Awin credentials, a live FruitStack connection, posts in actual forums, or revenue. Global crawling, an Amazon Creators API adapter, and adaptive optimization are **not yet implemented**. Unit tests deliberately use offline doubles rather than presenting simulated outcomes as live results.

This document also describes the intended direction of development. Not every capability discussed below has been implemented.

## Update v0.3.0 — Search coverage, link quality, and real attribution

The MCP core can evaluate purchase requests **individually against the same Awin product feed**, avoiding the loss of merchants caused by combined search terms or prematurely capped catalogs. Promotion queries support bounded pagination and report partial coverage. Feed language is not artificially equated with the buyer's market.

Execution uses a fast link-builder path, respects the product actually discussed by FruitStack, and distinguishes a content-based `fingerprint` from a `publication_key` that remains stable across retries. The `clickref` actually produced by Awin is returned for financial attribution.

Through `attribution_map`, `learn` can evaluate confirmed commissions and attributable costs per opportunity. Missing references are not invented, and payouts remain separately reported. CI tests the three actual tool calls with an MCP v2 client.

See [Release v0.3.0](docs/RELEASE_0.3.md), the [quickstart guide](docs/QUICKSTART.md), and the [MCP protocol tests](tests/test_mcp_protocol.py).

## Update v0.4.0 — Minimal posting history only

Before making expensive product and link requests, `find` and `execute` now check whether the same forum discussion has already been answered. The system stores **only the thread hash, timestamp, external post ID, and short-lived technical fields needed to prevent duplicate posts**. It does not store forum text, profiles, contacts, or KIGOR-style source data. A discussion already answered is deferred without blocking other opportunities.

The publication identifier is derived from the normalized thread URL and remains stable even if search IDs differ. The lookback window is configurable (180 days by default). See [minimal posting history and tests](docs/POST_HISTORY.md).

**Automatic forum registration still does not exist in MelonMe.** Neither account creation nor login is implemented. The publisher bridge has also not been demonstrated as a working live FruitStack connection.

## 1. Mission: A guerrilla business model, not an affiliate platform

MelonMe is a **guerrilla monetization tool**. It proactively identifies concrete, time-sensitive opportunities already emerging online, instead of buying advertising, planning large campaigns, or first building an audience. It operates in the language of each discussion and evaluates the actual target market separately from that language.

For example, someone in a suitable forum asks which vacuum cleaner works best for pet hair or requests alternatives to a particular pair of headphones. MelonMe identifies the question early, researches relevant products, provides a concise and useful comparison where appropriate, and can link to eligible, properly disclosed compensated offers. **Actual net earnings**, not post volume, determine which activities are worth repeating.

**The intended meaning of "guerrilla" explicitly includes unsolicited commercial outreach, including activity that recipients or platforms may classify as spam.** This intent is not relabeled as purely organic consumer advice. It creates significant business and platform risks (account suspension, removed content, forfeited commissions) that MelonMe must account for. Technical execution remains subject to the rules of the specific platform and partner program. Deception, fake accounts, fabricated personal experiences, and circumvention of technical safeguards are not intended features.

MelonMe covers **this one business model only**. It is not a replacement for FruitStack's central architecture, a general commerce or affiliate SaaS product, an advertising marketplace, an ad server, a publisher portal, or a buy-side advertising tool. Other business models belong in separate projects.

## 2. Three functions — The complete domain-level MCP interface

### `melonme.find(context)` — Identify and decide

- Identify **current** purchase-advice questions from legitimately accessible sources, prioritizing concrete buying intent, relevance to the discussion, and timing.
- Identify language and **sales/delivery market independently**; German-language content must not automatically imply Germany.
- Query existing offer sources that are genuinely accessible (for example, already connected Amazon or Awin capabilities), without claiming complete coverage.
- Verify whether a product is offered in the relevant market, whether a valid commission-bearing offer is possible, and whether the target channel permits the intended commercial response.
- Apply low-cost filters and existing knowledge **before** expensive model calls or product research.
- Return prioritized, evidence-backed opportunities or a specific local reason not to proceed at this time.

**No new partner registry as a separate system core.** Use existing credentials and FruitStack capabilities. An integration with partial access should be used for the capabilities that **actually work**; one unavailable capability must not disable the entire provider.

### `melonme.execute(opportunity)` — Take a useful action

- Check only the permissions and technical prerequisites necessary for **this particular action**.
- Build an honest, context-aware reply in the discussion's language from verifiable product data; a three-product comparison is **one possible format**, not a requirement.
- Compare suitability, drawbacks, compatibility, pricing, availability, and relevant ongoing costs. Commissions must never outweigh a product's actual suitability.
- Include compensated links **only when** both the specific affiliate arrangement and the intended publication permit them; clearly disclose commercial relationships.
- Publish through a demonstrably authorized interface. Where approval is required or permission remains unclear, return a usable draft **without forcing publication**.
- Return the actual external reply ID or a substantiated execution status. An internal "tool succeeded" message is not proof that anything was published.

**No blanket forum shutdown.** If a specific forum does not permit the action, only **that action in that location** is withheld. Other lawful channels remain available. A single question, community, or merchant integration must not trigger a system-wide shutdown.

### `melonme.learn(results)` — Measure money and improve decisions

- Ingest legitimately available click and transaction reports, plus **confirmed commissions, reversals, payouts, and actual attributable costs**.
- Strictly distinguish forecasts, clicks, reported purchases, approved commissions, and received funds. Unknown attribution must remain unknown.
- Identify which combinations of topic, language, market, channel, offer, timing, and answer format succeed **after costs**.
- Begin optimization with simple, explainable rules. Introduce more complex learning methods only when the evidence justifies them.
- Treat **NO_ACTION** and stopping an expensive, low-potential investigation as positive decisions when they save money.

**Economic objective:** Confirmed revenue minus attributable costs; actual cash payouts are reported separately. High profitability is a goal, not a fabricated guarantee.

## 3. Do not repeat the AVCOS mistakes

In AVCOS, providers were sometimes connected without consistently testing or using their actual capabilities. Missing information was mistaken for missing permission or missing offers. Blanket forum restrictions and rigid error handling turned isolated difficulties into global blockers.

MelonMe therefore follows **five operating rules only**:

1. **Test rather than assume.** A catalog listing is not proof of a working connection, but partial access is not total failure either. Where possible, make a real read-only capability call using an existing account and evaluate the actual response.
2. **Language ≠ country ≠ marketplace.** Product, merchant, delivery area, affiliate authorization, and tracking link must match a **specific** market. Do not guess missing data.
3. **Local failure stays local.** No result from one provider → check another existing, permitted provider. API failure → retry within limits or use an available alternative. Posting prohibited in one forum → do not post there. **No endless retries and no global STOP.**
4. **Unknown ≠ prohibited ≠ permitted.** Investigate unclear prerequisites precisely. Until permission for publication is positively established, withhold **only that public write action**; research, other partners, and other channels continue. Respect demonstrated prohibitions rather than circumventing them.
5. **External outcomes matter.** An actually published reply, a confirmed commission, and an actual payout require separate evidence. Never treat simulated earnings or internal activity metrics as business success.

**There is no additional multi-stage partner workflow engine, heavy approval registry, or global requirement to "activate everything first."** An action that is permitted and executable through an existing integration must not be blocked by artificial project milestones.

## 4. Lean integration with FruitStack

MelonMe is a **domain-specific MCP interface**, not a separate agent framework.

- **Reasoning, research, orchestration, model selection, credential security, operations monitoring, and long-term work state** remain with the appropriate FruitStack components, insofar as their actual interfaces are suitable and verified.
- MelonMe provides only the **three domain operations** and small adapters for the offer, publication, and outcome data those operations need.
- No second model-management system, universal router, system-wide ledger, parallel general-purpose scheduler, or duplicated agent framework.
- The service must remain usable with few calls. Expensive research is undertaken only when a cheap initial check identifies a plausible benefit.
- Partner information must not be committed to public repositories or placed in prompts. Existing secrets remain in the appropriate secure infrastructure.
- External write actions require specific authorization and duplicate-post prevention. Safeguards should be **narrow and concrete**, not an invented administrative program.

**Interface contract (conceptual):**  
`find` returns a compact opportunity with source and market context, offers actually discovered, and known uncertainties.  
`execute` returns `PUBLISHED`, `DRAFT_ONLY`, `NO_ACTION`, or a **local** error with verifiable evidence.  
`learn` returns an economic outcome summary and justified improvements to future selection.

The exact schema still needs verification against real FruitStack contracts and available partner capabilities. This README **does not claim that integration has already happened**.

## 5. Guerrilla operations: Speed, reach, and cost

MelonMe prioritizes **opportunities that can be handled quickly and have high economic potential**, while explicitly evaluating the risks of unwanted commercial outreach. Not every opportunity is suitable for publication; where publication is not permitted, research or draft generation may still be possible.

- **Be early, not intrusive.** Identify current questions and genuine information needs; do not revive closed discussions simply to advertise.
- **Multilingual and market-correct.** One language can span multiple countries; offers, currencies, delivery coverage, partner status, and links must actually fit.
- **Reuse what exists.** Prefer existing product sources, partner access, verified facts, and FruitStack infrastructure.
- **Cheap initial filter.** Avoid long agent chains for obviously outdated, uneconomic, or unusable opportunities.
- **Targeted alternatives.** When one source fails, check other permitted, genuinely accessible sources rather than building a new global architecture.
- **Quality over affiliate bias.** Omit unsupported product claims. Where appropriate, provide a short explanation rather than an elaborate table; do not manipulate recommendations to make them artificially positive.
- **Measure instead of inflating activity.** The number of forums, publisher accounts, models, MCP tools, or posts is not success. A traceable positive economic contribution is.

There are no predetermined success rates, claims of tenfold higher widget conversions, or fixed margins for particular product categories. Compare categories using real costs and commissions, not architecture-level assumptions.

## 6. Small implementation steps without artificial blockers

**Step A — Actually use what already exists.** Make **read-only tests** of the real FruitStack interfaces and already configured Amazon, Awin, or other partner integrations. Identify actual capabilities per market and inspect real responses. Specify exactly which capabilities are unclear, missing, or unauthorized, while keeping usable capabilities available in parallel.

**Step B — Make the three MCP functions executable.** Identify a real opportunity, research an appropriate offer correctly, and prepare a factually sound reply draft. Use test data to exercise failures, local fallbacks, time and cost limits, and `NO_ACTION`.

**Step C — Perform one permitted real action.** Where publication and affiliate use are specifically authorized, publish one approved reply and verify its external state. Otherwise return `DRAFT_ONLY` and continue with other permitted opportunities. No global forum shutdown.

**Step D — Measure outcomes and improve decisions.** Correctly attribute partner data, confirmed commissions, costs, and actual payouts. Improve simple economic selection rules using real outcomes. Make profitability claims only after an evidenced revenue cycle.

These steps describe development work, **not global approval gates** for capabilities already authorized.

## 7. Definition of success

MelonMe is technically useful when FruitStack can reliably call all three operations; language and market are correctly separated; existing partial integrations are genuinely used; local failures do not block unrelated opportunities; commercial replies are published only in permitted contexts; and outputs, results, and uncertainties are traceable.

MelonMe is **commercially successful** when permitted, real recommendations generate confirmed commissions and ultimately payouts exceeding their attributable costs. Each new decision should move toward this outcome at the lowest feasible cost.

**Core principle:** *Act quickly where we are permitted and genuinely able to. Fall back locally where something fails. Learn from actual money earned.*

---

**Status clarification:** v0.3.1 describes the target concept. An initial executable MCP core has been added, but no live partner operation, host integration, or real revenue has been verified. Earlier concepts remain available in Git history.

## License

**No license has been granted for this repository at this time.** Public visibility on GitHub does not make MelonMe open-source software or grant general permission to use, modify, or redistribute its code. No `LICENSE` file is included.
