# WearItRight — Project Implementation Plan

> **Design phase:** Complete
> **Implementation window:** 3 weeks (15 working days)
> **Assumed team:** 4 developers (Dev A, B, C, and D) + 1 UI/UX Designer (part-time, Weeks 1–3)
> **All diagrams and requirements are finalised** — use case, class, sequence, ER, functional, non-functional, high-level, and low-level artefacts serve as the implementation contract.

---

## Project Summary

WearItRight is a web application that recommends complete, context-aware outfits based on weather, event type, and personal style preferences, and connects users to the best available purchase prices across multiple shopping providers.

---

## Milestone Overview

| Milestone | Target Day | Description |
|---|---|---|
| M1 — Foundation Ready | Day 4 | Infrastructure, database, and auth live |
| M2 — Recommendation Core Live | Day 8 | Weather, context, and recommendation engine functional |
| M3 — Shopping and UI Complete | Day 12 | Shopping integration, full UI, and favorites working |
| M4 — Production Release | Day 15 | Quality, resilience, security, and deployment complete |

---

## Phase 1 — Foundation and Identity (Week 1, Days 1–4)

**Goal:** Working infrastructure, data layer, and authentication service ready for feature work.

| # | Task | Owner | Duration | Depends On | Requirement |
|---|---|---|---|---|---|
| 1.1 | Initialise repository, branching strategy, CI pipeline (lint, test, build) | Dev A | 0.5 day | — | NFR-27, NFR-29 |
| 1.2 | Provision dev, staging, and production environments; configure secrets management | Dev A | 0.5 day | 1.1 | NFR-10, NFR-29 |
| 1.3 | Implement database schema from ER diagram — all tables, PKs, FKs, indexes, and migrations | Dev B | 1.5 days | 1.2 | LLR 12.1 |
| 1.4 | Implement AuthService — registration, login, logout, JWT session management, and role enforcement | Dev A | 1.5 days | 1.3 | FR-01, FR-02, LLR 1.1–1.3, NFR-11–13 |
| 1.5 | Implement password reset flow with signed email token and EmailClient adapter | Dev C | 0.5 day | 1.4 | FR-03, LLR 1.4 |
| 1.6 | Implement ConsentRecord creation on registration; geolocation consent gate | Dev C | 0.5 day | 1.4 | LLR 9.5, NFR-15 |
| 1.7 | Implement ProfileService — preferences, sizes, and exclusions CRUD (all normalised child tables) | Dev D | 1.5 days | 1.3 | FR-04, FR-05, LLR 1.5–1.7 |
| 1.8 | UI: Registration, login, password reset, and profile setup screens (responsive, accessible) | Designer + Dev B | 1 day | 1.4, 1.7 | FR-26, FR-27, NFR-21–25 |

> **Note:** Dev C and Dev D are unblocked on Day 2 once Dev B delivers the schema (1.3). Dev A completes AuthService (1.4) by end of Day 3, unblocking 1.5, 1.6, and 1.8.

**Phase 1 Deliverables**

- Deployed database with all identity and profile tables
- Working register / login / logout / password reset API
- Profile and exclusion management API
- Responsive and accessible UI screens for account and profile flows

---

## Phase 2 — Recommendation Engine (Week 2, Days 5–8)

**Goal:** Core recommendation pipeline functional end-to-end — location, weather, event context, generation, ranking, explanations, and confidence tips.

| # | Task | Owner | Duration | Depends On | Requirement |
|---|---|---|---|---|---|
| 2.1 | Implement WeatherApiAdapter — integrate weather provider, parse response into WeatherSnapshot | Dev A | 1 day | 1.2 | FR-07, LLR 2.3, LLR 13.1 |
| 2.2 | Implement weather response cache with configurable TTL (default max 30 min) | Dev A | 0.5 day | 2.1 | LLR 13.4, NFR-09 |
| 2.3 | Implement location context input — manual entry and consent-gated browser geolocation | Dev B | 0.5 day | 1.6 | FR-06, LLR 2.1–2.2 |
| 2.4 | Implement event context input — event type, dress code, and event time selectors | Dev C | 0.5 day | — | FR-08, LLR 2.4–2.6 |
| 2.5 | Implement RecommendationService core — generate ≥ 3 outfit candidates (top, bottom, footwear, accessory) | Dev C | 1 day | 2.1, 2.3, 2.4 | FR-09, FR-10, LLR 3.1–3.2 |
| 2.6 | Implement exclusion filter, weather rules (layering threshold, rain-resistant threshold), and relevance ranking | Dev A | 1 day | 2.5 | FR-11, LLR 3.3–3.6 |
| 2.7 | Implement recommendation explanation and confidence style tip generation per outfit | Dev D | 0.5 day | 2.5 | FR-12, FR-13, LLR 3.7–3.8 |
| 2.8 | Implement regenerate action; persist RecommendationRequest and all child records with timestamps | Dev D | 0.5 day | 2.6, 2.7 | FR-14, LLR 12.2–12.3 |
| 2.9 | UI: Context input screens (location, event) and recommendation results cards with "Why this outfit" panel | Designer + Dev B | 1 day | 2.5 | FR-15, FR-16, LLR 4.1–4.5 |
| 2.10 | Unit tests for recommendation ranking, exclusion filter, and weather rule logic (≥ 70% coverage) | Dev C | 0.5 day | 2.6 | NFR-28 |

**Phase 2 Deliverables**

- Full recommendation pipeline API (context → weather → generate → rank → explain)
- Outfit cards UI with "Why this outfit" section and confidence tips
- Regenerate button functional
- Unit test coverage ≥ 70% on recommendation business logic

---

## Phase 3 — Shopping Integration, UI Completion, and Favorites (Week 3, Days 9–12)

**Goal:** Shopping comparison functional; product filtering, sorting, and favorites working; UI complete and polished.

| # | Task | Owner | Duration | Depends On | Requirement |
|---|---|---|---|---|---|
| 3.1 | Implement ShoppingApiAdapter for Provider 1 — product search, price, stock, and product URL | Dev A | 1 day | 1.2 | FR-17, FR-18, LLR 5.1–5.2, LLR 13.2 |
| 3.2 | Implement ShoppingApiAdapter for Provider 2 (runs in parallel with 3.1) | Dev B | 1 day | 1.2 | FR-17, FR-18, LLR 13.2 |
| 3.3 | Implement ShoppingService — ProductMatch generation, multi-provider offer retrieval, currency normalisation | Dev D | 0.5 day | 3.1, 3.2 | FR-17, FR-18, LLR 5.1–5.3 |
| 3.4 | Implement best-price identification, stock exclusion default, PriceComparisonResult persistence | Dev D | 0.5 day | 3.3 | FR-18, FR-19, LLR 5.4–5.6 |
| 3.5 | Implement FilterSortService — filter by price, brand, size, color, store; four sort options | Dev C | 0.5 day | 3.3 | FR-21, FR-22, LLR 6.1–6.3 |
| 3.6 | Implement FavoritesService — save and remove outfit and item, list with saved timestamps | Dev C | 0.5 day | Phase 1 | FR-23, FR-24, FR-25, LLR 7.1–7.4 |
| 3.7 | UI: Price comparison cards, best-price badge, stock indicator, and external store redirect | Designer + Dev B | 1 day | 3.4 | FR-19, FR-20, LLR 5.4–5.5 |
| 3.8 | UI: Filter panel, sort controls, and favorites list with timestamps | Dev C | 0.5 day | 3.5, 3.6 | FR-21–25, LLR 7.4 |
| 3.9 | Accessibility pass — keyboard navigation, alt text, and colour contrast ≥ 4.5:1 across all screens | Designer + Dev D | 0.5 day | All UI | FR-27, NFR-21–23, LLR 11.1–11.4 |
| 3.10 | Integration tests for shopping pipeline (mocked providers) and favorites service | Dev A | 0.5 day | 3.4, 3.6 | NFR-28 |

> **Note:** Tasks 3.1 and 3.2 are independent and run in parallel — Dev A owns Provider 1, Dev B owns Provider 2. Dev C and Dev D begin service-layer work (3.5, 3.6, 3.3) in parallel from Day 9.

**Phase 3 Deliverables**

- Live product matching and best-price comparison from two shopping providers
- Filtering, sorting, and external retailer redirect functional
- Favorites save, remove, and list working with persisted timestamps
- All UI screens accessible and responsive at ≥ 360 px width

---

## Phase 4 — Quality, Security, Resilience, and Deployment (Week 3, Days 13–15)

**Goal:** Production-ready: resilience policies, security hardening, audit logging, observability, performance testing, and live deployment.

| # | Task | Owner | Duration | Depends On | Requirement |
|---|---|---|---|---|---|
| 4.1 | Implement FeedbackService — loading indicators, actionable error messages, weather fallback prompt | Dev B | 0.5 day | All services | FR-28, LLR 8.1–8.3, NFR-20 |
| 4.2 | Implement ResiliencePolicy — per-provider retry, timeout, and circuit breaker; graceful degradation | Dev A | 1 day | 3.1, 3.2 | FR-31, LLR 10.3, LLR 13.3, NFR-06, NFR-07 |
| 4.3 | Implement AuditLog writes — login, logout, password reset, recommendation request, account deletion events | Dev C | 0.5 day | Phase 1–2 | FR-32, LLR 9.7, NFR-17 |
| 4.4 | Implement MonitoringService — latency, error rate, and API health metrics; alerting on threshold breach | Dev D | 0.5 day | 4.2, 4.3 | NFR-18, NFR-05 |
| 4.5 | Security hardening — HTTPS enforcement, input validation, XSS and CSRF protections, OWASP Top 10 review | Dev A | 1 day | All | FR-29, LLR 9.1–9.4, NFR-10, NFR-12, NFR-14 |
| 4.6 | Implement account deletion cascade — purge all personal data tables and invalidate all sessions | Dev B | 0.5 day | Phase 1 | FR-30, LLR 9.6, NFR-16 |
| 4.7 | Performance testing — verify P95 recommendation response < 5 s and filter/sort < 2 s under simulated load | Dev D | 0.5 day | 4.2 | NFR-01, NFR-03, LLR 10.1 |
| 4.8 | End-to-end test suite covering primary flows (register → profile → recommendation → shopping → favorites) | Dev C | 0.5 day | All | NFR-27, NFR-28 |
| 4.9 | Final UI QA — cross-browser (Chrome, Edge, Firefox, Safari latest 2 versions each), mobile and desktop | Dev B | 0.5 day | All UI | NFR-24, NFR-25 |
| 4.10 | Production deployment — automated pipeline, smoke tests, and rollback verification | Dev A | 0.5 day | 4.7, 4.8 | NFR-29, NFR-30 |

> **Note:** All four developers operate in parallel throughout Phase 4. Dev A handles infrastructure concerns (resilience and security), while Dev B, C, and D cover user experience, audit, and testing tracks concurrently.

**Phase 4 Deliverables**

- Resilience policies active for all external API calls
- Complete audit log and operational monitoring dashboards
- OWASP Top 10 security checklist passed
- Account deletion fully purging all personal data
- Successful production deployment with rollback verified

---

## Full Timeline at a Glance

```
Week 1  │ Days 01–04 │ Phase 1 — Foundation and Identity
Week 2  │ Days 05–08 │ Phase 2 — Recommendation Engine
Week 3  │ Days 09–12 │ Phase 3 — Shopping, UI, and Favorites
Week 3  │ Days 13–15 │ Phase 4 — Quality, Security, and Deployment
```

| Phase | Working Days | Dev A effort | Dev B effort | Dev C effort | Dev D effort | Designer effort |
|---|---|---|---|---|---|---|
| Phase 1 — Foundation | 4 days | 2.5 days | 2.0 days | 1.0 day | 1.5 days | 0.5 day |
| Phase 2 — Recommendation | 4 days | 2.5 days | 1.0 day | 2.0 days | 1.0 day | 0.5 day |
| Phase 3 — Shopping and UI | 4 days | 1.5 days | 1.5 days | 1.5 days | 1.5 days | 1.0 day |
| Phase 4 — Quality and Deploy | 3 days | 2.5 days | 1.5 days | 1.0 day | 1.0 day | — |
| **Total** | **15 days** | **9.0 days** | **6.0 days** | **5.5 days** | **5.0 days** | **2.0 days** |

---

## Parallel Work Schedule

| Days | Dev A | Dev B | Dev C | Dev D |
|---|---|---|---|---|
| 1 | Repo, CI, and environments (1.1+1.2) | DB schema start (1.3) | — | — |
| 2–3 | AuthService (1.4) | DB schema complete (1.3) | — | ProfileService (1.7) |
| 4 | AuthService complete | Account UI screens (1.8) | Password reset and consent record (1.5+1.6) | ProfileService complete |
| 5–6 | WeatherApiAdapter and cache (2.1+2.2) | Location context (2.3) | Event context and recommendation core (2.4+2.5) | Explanation, tips, and regenerate (2.7+2.8) |
| 7–8 | Exclusion filter, ranking, and rules (2.6) | Recommendation UI cards (2.9) | Recommendation core complete; unit tests (2.10) | Regenerate complete; available support |
| 9–10 | ShoppingApiAdapter Provider 1 (3.1) | ShoppingApiAdapter Provider 2 (3.2) | FilterSortService and FavoritesService (3.5+3.6) | ShoppingService and best-price logic (3.3+3.4) |
| 11–12 | Integration tests and accessibility (3.10+3.9) | Price comparison UI (3.7) | Filter/sort/favorites UI (3.8) | Best-price complete; accessibility support (3.9) |
| 13 | ResiliencePolicy (4.2) | FeedbackService and account deletion (4.1+4.6) | AuditLog and E2E tests start (4.3+4.8) | MonitoringService and performance testing (4.4+4.7) |
| 14 | Security hardening (4.5) | Cross-browser QA (4.9) | E2E tests complete (4.8) | Performance testing complete (4.7) |
| 15 | Production deployment (4.10) | Smoke tests and rollback verification | Final QA sign-off | Final QA sign-off |

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Shopping provider API access or approval delayed | Medium | High | Build mock adapters in Phase 3; swap real credentials when available without rework |
| Weather API rate limits exceeded | Low | Medium | 30-minute cache (LLR 13.4) reduces call volume; manual weather fallback already designed |
| Recommendation quality insufficient for demo | Medium | High | Ranking algorithm is isolated, unit-tested, and uses configurable scoring weights |
| UI responsiveness takes longer than estimated | Low | Medium | Dedicated designer plus two devs available for UI in Phase 3; component library reduces effort |
| Security review reveals critical gaps late | Low | High | OWASP checklist applied per phase throughout, not deferred entirely to Week 3 |
| Performance target of P95 < 5 s not met | Low | Medium | Weather and product offer caching already in place; targeted profiling in Phase 4 |
| Scope creep from stakeholder feedback | Medium | Medium | Changes assessed against FR/NFR contract; out-of-scope items deferred to a follow-up sprint |

---

## Definition of Done

A task is considered complete when all of the following are true:

1. Code is reviewed and merged to the main branch via pull request
2. Automated tests (unit and/or integration as applicable) pass in CI
3. The linked functional or non-functional requirement is verifiably met
4. No critical lint or security policy violations remain
5. UI tasks additionally pass responsive (≥ 360 px) and accessibility (WCAG 2.1 AA) checks

---

## Design Artefact Reference

| Artefact | Path | Purpose |
|---|---|---|
| Business Requirements | `design/requirements/buisiness_requirements.txt` | Product vision and goals |
| High-Level Requirements | `design/requirements/high_level_requirements.txt` | System-level capabilities (12 HLRs) |
| Low-Level Requirements | `design/requirements/low_level_requirements.txt` | Detailed behavioural rules (13 sections) |
| Functional Requirements | `design/requirements/functional_requirements.txt` | FR-01 to FR-32 |
| Non-Functional Requirements | `design/requirements/non_functional_requirements.txt` | NFR-01 to NFR-32 |
| Use Case Diagram | `design/docs/usecase.puml` | Actor and use case scope |
| Class Diagram | `design/docs/class.puml` | Domain model and service interfaces |
| Sequence Diagram | `design/docs/sequence.puml` | All application interaction flows |
| ER Diagram | `design/docs/ER.puml` | Relational data model |
