# Default Sort Algorithm v3.4

**Version:** 3.4  
**Date:** October 2026  
**Status:** Approved pre-launch public specification  
**License:** MIT

## Status

This is Really Global's approved public specification for the Default Sort algorithm to be implemented for platform launch. It supersedes v3.3. Really Global has not launched, and Default Sort is not yet running in production. Publication of this specification does not claim that the product code has already been implemented.

Once Default Sort is implemented, the running algorithm and this public specification must remain in lockstep. A difference between the running algorithm and the public specification is a bug.

## Why a default order is necessary

Really Global is a marketplace. Every marketplace must place results in an order. If the product does not define that order, the database, cache, or prior activity still creates one accidentally. An accidental or changing order is not neutral. It is harder to explain, less useful to clients, and can give random advantages to providers who happen to appear first.

For this algorithm, neutrality does not mean randomness. Neutrality means:

- the same disclosed rules apply consistently;
- Really Global does not choose a provider for an individual client;
- Really Global does not decide who is clinically best;
- providers cannot buy a score, tier, or position; and
- the algorithm does not direct diagnosis, treatment, scope of practice, or professional judgment.

Default Sort applies disclosed marketplace rules to attributed facts and operational signals. It orders eligible providers; it does not endorse one provider over another or select a provider for the client.

## Sources of the inputs

| Input source | Examples |
|---|---|
| Provider-attested information | provider category, experience, credentials, calendar availability, Talk Now status, enabled platform capabilities |
| Client-attributed information | star ratings and reviews |
| Independent third-party outcome | whether the provider completed the applicable verification process and received Verified status |
| Platform-observed operational event | Talk Now answer timing and misses, from rings to a named provider and from "Anyone available now" fan-out rings alike, and accepted-session completion under the disclosed service rules |

Really Global applies the formula to these inputs. It does not turn them into a clinical judgment about competence, quality, or suitability for a particular client.

## Overview

Default Sort runs as a three-stage pipeline:

1. **Filter** — determines which otherwise-eligible providers are currently visible.
2. **Tier** — groups visible providers by Verified status and current Talk Now availability.
3. **Score** — orders providers within each tier using five base-score factors and, only for active Talk Now providers, the Talk Now Reliability multiplier.

The stages run in that order. Tier order always defeats within-tier score. A client-selected sort, client filters, semantic relevance, an explicit matching result, or the client's own choice may change or override Default Sort as described below.

## Stage 1: Filter

Default Sort runs only after a provider satisfies Really Global's applicable account, profile, connection, eligibility, and visibility requirements. Those requirements decide who may appear. Default Sort decides the order of providers who may appear.

An otherwise-eligible provider appears only if at least one of these conditions is true:

- the provider has at least one bookable calendar slot within the next 14 days; or
- the provider's Talk Now toggle is active for the present hour.

If neither condition is true, the provider is not shown. There is no unavailable provider state in the search-results list.

## Stage 2: Tier

Providers who pass Stage 1 enter one of four tiers:

| Tier | Verified status | Talk Now status |
|---|---|---|
| 1 | Verified | active now |
| 2 | Verified | not active; calendar availability only |
| 3 | Not Verified | active now |
| 4 | Not Verified | not active; calendar availability only |

Tier order is fixed. Every Tier 1 provider appears before every Tier 2 provider, every Tier 2 provider before every Tier 3 provider, and every Tier 3 provider before every Tier 4 provider. A perfect score in a lower tier does not move a provider above a provider in a higher tier.

Verified status is the outcome of an independent verification process. Verification is a paid service from Certn, an independent third-party verification company. Verification is voluntary: the provider chooses whether to purchase it and pays Certn. The fee goes to Certn, not to Really Global, and Really Global keeps no margin on it. The amount is calculated from what is on the provider's own profile, because each listed licence, each education credential, and any background check is a separate check with its own cost. It is available to every provider on identical terms. Certn's result decides Verified status. Really Global receives the result needed to apply the badge and tier rule; it does not decide whether the provider passed. Paying the fee does not buy Verified status or any position, and no provider can obtain a higher position by paying a greater amount.

## Stage 3: Score

Within each tier:

    final_score = base_score × reliability_multiplier

The base score ranges from 0 to 90 points. The Reliability multiplier is either neutral or 1.10, and it is used only when ordering active Talk Now providers against other active Talk Now providers. The maximum effective final score is 99.

## The five base-score factors

| # | Factor | Maximum |
|---|---|---:|
| 1 | Amount of Availability | 20 |
| 2 | Professional Preparation — Experience | 20 |
| 3 | Professional Preparation — Credential Breadth | 20 |
| 4 | Client Reviews, Bayesian-weighted | 20 |
| 5 | Real-Time Audio Translation Enablement | 10 |
|  | **Total** | **90** |

Factors 2 and 3 are the two equal halves of Professional Preparation, worth 40 points together.

### Factor 1: Amount of Availability — 0 to 20 points

Let slots equal the number of bookable calendar slots in the next 14 days.

    if slots >= 2:
        raw = 20 + min(slots - 2, 18) × (80 / 18)
    else:
        raw = 0

    availability_points = (raw / 100) × 20

A provider with zero or one slot receives zero points. A provider with two slots begins earning points. Each additional slot through 20 adds the same incremental value. The factor reaches its 20-point cap at 20 slots; additional slots do not add points.

The source is the provider's connected calendar. The value is dynamic.

### Factor 2: Professional Preparation — Experience — 0 to 20 points

The provider's category selects one experience field and its existing tier scale:

| Provider category | Source field | Raw-score scale |
|---|---|---|
| Therapist, every permission status | Years in Practice | 0–2 years = 50; add 10 for each existing experience tier; cap at 100 for 20+ years |
| Nurses & More, every permission status | Years in Practice | 0–2 years = 50; add 10 for each existing experience tier; cap at 100 for 20+ years |
| Coach | Completed Coaching Hours | 0–500 hours = 40; add 10 for each existing experience tier; cap at 100 for 3,000+ hours |
| Mentor | Completed Practice Hours | 0–500 hours = 40; add 10 for each existing experience tier; cap at 100 for 2,000+ hours |

    experience_points = (raw_score / 100) × 20

License, registration, permit, certification, under-supervision status, or no-license-required status does not select the scale and does not exclude a provider from this factor. A therapist uses the Therapist scale whether licensed, under supervision, or practicing in a place where a license is not required. The same rule applies to Nurses & More providers. If the applicable source field is missing, this factor returns zero until the provider supplies it.

Really Global applies the disclosed scale to the value the provider attested to. It does not independently decide how experienced the provider is.

### Factor 3: Professional Preparation — Credential Breadth — 0 to 20 points

Credential Breadth uses three yes-or-no groups. Each group can count only once:

| Group | Qualifying condition |
|---|---|
| Permission to practice | at least one current License, Registration, or Permit record that is complete and eligible for public display |
| Academic education | at least one Academic Degree record that is complete and eligible for public display |
| Professional training | at least one current Professional Certificate record that is complete and eligible for public display |

Let n equal the number of qualifying groups represented:

| Groups represented | Points |
|---:|---:|
| 0 | 0 |
| 1 | 10 |
| 2 | 15 |
| 3 | 20 |

The formula counts groups, never individual records. One license and five licenses produce the same Permission-to-practice group. One degree and several degrees produce the same Academic-education group. One certificate and several certificates produce the same Professional-training group.

Except for the migrated records described below, only complete records eligible for public display can establish a group. An expired License, Registration, Permit, or Professional Certificate does not count. A credential marked as not expiring may count while it remains eligible for public display. An Academic Degree records completed education and does not require a current-practice status. Missing, incomplete, hidden, or otherwise ineligible records do not count.

**Migrated credential records.** Once credential records are read from the unified credential record (`CREDENTIAL_SOURCE_MODE=unified`), a record written by the one-time migration from the legacy credential record, and not yet edited by the provider, counts the way the legacy record it came from counted: a migrated License establishes Permission to practice, a migrated Academic Degree establishes Academic education, a migrated Professional Certificate establishes Professional training, and a migrated Professional Membership establishes no group. Whether a migrated License or Professional Certificate is current is decided by the expiry year on the legacy record. Completeness is not required for these records. Once the provider edits a migrated record, that record follows the complete-record rule above. A record the provider creates is never treated as migrated.

Professional Membership records do not count. Under Supervision and No license required are statuses, not credential records, and do not establish a group. A provider in a jurisdiction where no permission-to-practice credential exists may earn up to 15 points through Academic education and Professional training.

The three groups are deliberately not weighted against one another. Really Global does not decide that one degree, license, permit, registration, or certificate is harder, better, more relevant, or more valuable than another.

Credential Breadth is separate from the Verified gate. Credential Breadth reads eligible provider-supplied credential records. The Verified gate consumes the independent verification outcome. Credential Breadth does not make an unverified credential verified.

### Factor 4: Client Reviews — Bayesian-weighted, 0 to 20 points

Default Sort uses the same official star average and rating count used by the Review System. It does not reclassify reviews or rebuild the provider's average from raw review records.

Definitions:

- v = number of ratings included in the provider's official star average
- R = provider's official mean star rating
- m = 5, the Default Sort prior-strength constant
- C = platform mean across the same included-rating population, recomputed nightly

    if v == 0:
        weighted_rating = C
    else:
        weighted_rating = (v / (v + m)) × R + (m / (v + m)) × C

    reviews_points = min(20, max(0, (weighted_rating - 1) × 5))

The Review System's inclusion rules control:

- a published star-only review counts even if it has no written review card;
- a mixed review containing provider feedback and a technical issue counts normally;
- a confirmed tech-only review does not count;
- a voided or removed review does not count; and
- Default Sort does not independently decide which reviews count.

The value m = 5 stabilizes the formula. It is not a point where reviews suddenly receive full weight. At five ratings, R and C each contribute half of the weighted rating. As v grows, the provider's own average gradually contributes more.

The Review System's separate five-review rule applies only to whether the portal displays detailed patterns about what clients said was a fit. It does not hide the star-rating summary and does not define v, R, or m.

### Factor 5: Real-Time Audio Translation Enablement — 0 or 10 points

    translation_points = 10 if translation is enabled, otherwise 0

Translation is enabled by default for providers at account creation. A provider may opt out. Therefore, the provider receives 10 points in the default state and zero points after opting out.

The points apply uniformly in every search-results page where the provider appears. This is a capacity signal, not a claim about language fluency or clinical quality. It measures whether the provider has enabled a platform capability that can expand the population the provider can serve.

The factor is binary because the account setting is either on or off. It is additive rather than a tier gate so Really Global does not declare translated service better or worse than native-language service. The value is meaningful but capped: it cannot override tier order and contributes at most 10 of the 90 base-score points.

## Talk Now Reliability Score and multiplier

The Reliability Score measures Talk Now answer performance over a rolling 30-day window. It does not measure scheduled-session quality and does not apply outside the active Talk Now tiers.

### Eligible answer events

Rings to a named provider and Top Nav "Anyone available now" fan-out rings are scored the same way, under the same 60-second window. For a Reliability Score-eligible Talk Now ring from either entry point:

| Event | Definition | Answer points |
|---|---|---:|
| Fast answer | answered from 0 through 30 seconds | 100 |
| On-Time answer | answered after 30 seconds and before the 60-second timeout | 85 |
| Miss | not answered before the 60-second timeout | 0 |

There is no decline input because Talk Now is answer-only. A ring stopped before the 60-second timeout because another provider answered, the client cancelled, or the request reached its 3-minute stop is neither an answer nor a miss and creates no Reliability Score event. Every ring event stays tagged with its entry point for analytics, but the entry point does not change how the event is scored. Fan-out answers and misses count toward the five-event history threshold and toward the miss-count suspension rules exactly as named-provider answers and misses do. Accepted sessions that reach in progress may feed Session Completion Rate regardless of entry point.

    answer_performance = 30-day average of eligible answer points
    reliability_score = (answer_performance × 0.90) + (session_completion_rate × 0.10)

### Multiplier scope

| Provider state | Multiplier treatment |
|---|---|
| Active Talk Now and Reliability Score 90–100 | 1.10 Boosted multiplier |
| Active Talk Now and Reliability Score below 90 | 1.00 neutral multiplier |
| Active Talk Now with fewer than five eligible events | 1.00 neutral multiplier and insufficient-history state |
| Talk Now off, never enabled, or suspended | no Reliability multiplier; base score alone |

The multiplier applies only inside Tier 1 or Tier 3 when ordering active Talk Now providers against other providers in the same Talk Now tier. It never carries into Tier 2 or Tier 4. A future scheduled-reliability signal would require separate review; Talk Now Reliability is not used as a proxy for it.

### Talk Now suspension

Talk Now suspension is driven by the miss-count rules, not by the Reliability Score crossing a threshold. Misses from named-provider rings and from fan-out rings count in the same way:

- two misses in a rolling seven-day window trigger a seven-day Talk Now suspension;
- five incidents in 30 days trigger a 30-day Talk Now suspension and required Reliability Recertification.

Talk Now suspension is not platform suspension. The Talk Now toggle is forced off and the Talk Now button is hidden, but the provider keeps the profile, scheduled bookings, payments, portal access, and other platform features. If calendar availability remains, the provider moves from Tier 1 to Tier 2 or from Tier 3 to Tier 4 and is ordered by base score alone. No additional 0.70 penalty and no 60-day recovery penalty apply.

When suspension ends and any required recertification is complete, a provider who re-enables Talk Now returns to the Talk Now tier. The live rolling score applies immediately.

### Provider-facing standing

The internal multiplier table is not the provider-facing display. The provider portal uses one standing:

- **Boosted** — fast and reliable, receiving the 1.10 search boost, with no active miss warning.
- **Reliable** — in good standing, answering within the 60-second window with no miss in the current rolling seven-day window.
- **On Notice** — one miss in the rolling seven-day window; one more miss will pause Talk Now for seven days.
- **Suspended** — Talk Now is paused under the miss-count rules.

If the speed-based standing and the active warning disagree, the warning controls what the provider sees. The sort boost itself remains governed by the live score.

## Tiebreakers

When two providers in the same tier have the same final score:

1. most recent profile update first; then
2. provider ID ascending for deterministic stability.

## End-to-end ordering

    visible = otherwise_eligible providers with:
        a bookable slot in the next 14 days
        OR Talk Now active now

    assign each visible provider to Tier 1, 2, 3, or 4

    for tiers 1 through 4 in order:
        base_score = availability
                   + experience
                   + credential_breadth
                   + reviews
                   + translation

        if this is an active Talk Now tier:
            final_score = base_score × applicable Talk Now multiplier
        else:
            final_score = base_score

        sort by final_score descending,
                profile update time descending,
                provider ID ascending

    concatenate Tier 1, then Tier 2, then Tier 3, then Tier 4

## Worked example

Example provider: Verified Therapist, Talk Now active, 10 calendar slots in 14 days, 20+ years in practice, two Credential Breadth groups, 18 ratings with an official mean of 4.6, platform mean C of 4.5, Reliability Score of at least 90, and translation enabled.

| Component | Points |
|---|---:|
| Availability | 11.1 |
| Experience | 20.0 |
| Credential Breadth, two groups | 15.0 |
| Reviews | 17.9 |
| Translation enabled | 10.0 |
| **Base score** | **74.0** |

The provider is in Tier 1. The Boosted multiplier applies:

    74.0 × 1.10 = 81.4 final score within Tier 1

If translation were disabled, the base score would be 64.0 and the final score would be 70.4. If the provider's active Talk Now Reliability Score were below 90, the neutral 1.00 multiplier would apply.

## Where Default Sort applies

Default Sort applies when the platform displays a provider list without an explicit user-selected order, including:

- provider directory and navigation pages;
- specialty and location pages;
- navigation-style search results where there is no relevance signal; and
- the default Find Matches order before a client supplies matching preferences.

Default Sort does not run by itself when:

- a user selects a different sort, such as price or most reviews;
- semantic search supplies the primary relevance signal; or
- Find Matches has explicit client preferences to apply.

For semantic search, tier order still dominates. Semantic relevance is the primary within-tier key, and Default Sort final score is the tiebreaker. The Stage 1 visibility filter is applied after retrieval because calendar availability and Talk Now state change too quickly to be treated as static search metadata.

A user-selected sort changes the order of the providers who pass Stage 1. It does not change who passes Stage 1.

### Talk Now "Anyone available now" fan-out

Discovery Entry Talk Now (the Top Nav "Anyone available now" option) uses Stage 1 eligibility and tier composition to identify a candidate pool. The pool criteria, including the client's price maximum, and the ring timing are owned by Really Global's Talk Now Discovery Entry rules.

Within the candidate pool, providers are rung in Default Sort order:

1. active Talk Now Verified providers (Tier 1) before active Talk Now Not Verified providers (Tier 3), so a Verified provider is always rung before any Not Verified provider; then
2. within each tier, by final_score, using the same Reliability multiplier as above; then
3. by the standard tiebreakers.

The order is computed once when the fan-out starts. There is no separate fairness algorithm, no randomness, no cooldown or rotation after a session, no last-call-time decay, and no separate allocation for providers with insufficient history. Native speakers and translation-enabled providers are treated by the same rule: the value of translation enablement is counted once, in Factor 5, and reaches fan-out order only through final_score. Fan-out rings create Reliability Score events exactly like named-provider rings.

When 9 or more Verified providers have Talk Now active in a pool, Not Verified providers will rarely be reached in fan-out. This is the same outcome Default Sort produces on search results pages.

## Cold start

There is no new-provider boost. New providers use the same rules as everyone else:

| Factor | Cold-start treatment |
|---|---|
| Availability | live calendar signal |
| Experience | provider-attested value; missing value earns zero |
| Credential Breadth | eligible public credential groups; no groups earn zero |
| Reviews | zero ratings produce the platform mean C through Bayesian shrinkage |
| Translation | default-on providers receive 10 points; providers who opt out receive zero |
| Reliability | fewer than five eligible Talk Now events receive the neutral 1.00 multiplier |

## Clinical neutrality

The algorithm organizes a marketplace. It does not practice medicine or decide what care is appropriate. In particular:

- availability measures bookable capacity;
- experience applies a disclosed scale to a provider-attested field;
- Credential Breadth counts broad public credential groups without judging credential quality;
- reviews aggregate client-assigned ratings under the Review System's rules;
- translation reads an account setting;
- reliability measures performance against the provider's chosen Talk Now availability commitment;
- Verified status consumes an independent verification outcome; and
- Talk Now tiering reads the provider's current service setting.

None of these rules requires Really Global to evaluate diagnosis, treatment, clinical competence, scope of practice, or suitability for a specific client.

## No paid placement

Providers cannot purchase a score, factor weight, tier, or position, and no provider can pay Really Global for placement. Verification is a voluntary, paid service from Certn: the provider pays Certn, and the fee goes to Certn, not to Really Global. Verified status affects tier, but Certn's result decides it. The fee does not buy Verified status or any position, cannot be increased to obtain a better position, and does not allow bidding.

## Version history

- **v3.4, October 2026.** Talk Now "Anyone available now" fan-out rings now count toward the Reliability Score exactly like rings to a named provider: Fast, On-Time, or Miss within the same 60-second window, with the same miss consequences, and counting toward the five-event history threshold. A ring stopped early creates no event. This reverses the v3.3 rule that fan-out non-answers were operational-only. Fan-out ring order now uses Default Sort order within the candidate pool (Tier 1 before Tier 3, then final_score, then tiebreakers), replacing the separate fan-out fairness logic, and the specification discloses that Not Verified providers will rarely be reached when 9 or more Verified providers are active. Verification wording is corrected: verification is a paid service from Certn, the fee goes to Certn and not to Really Global, and paying does not buy Verified status or position. Carries forward the v3.3 migrated credential records amendment. No factor, weight, point value, gate, tier, multiplier value, or tiebreaker changes.
- **v3.3 amendment, October 2026.** Adds the migrated credential records exception to Credential Breadth, so that moving to the unified credential record does not change any provider's credential groups (RGDEV-1927, comment 34511). No other rule, weight, or point value changes.
- **v3.3 — August 2026.** Replaces record-count credential scoring with the approved Credential Breadth formula: three unweighted groups, counted once each, scored 0/10/15/20. Expands the Experience factor to every Therapist and Nurses & More permission status while preserving category-specific experience fields. Incorporates the corrected Talk Now-local Reliability model, neutral cold start, Review System population alignment, 97-language context, and truthful pre-launch status. Supersedes the unpublished v3.2 target.
- **v3.1 — May 2026.** Added Real-Time Audio Translation Enablement as a fifth base-score factor, raising the base-score maximum from 80 to 90.
- **v3.0 — April 2026.** Introduced Filter → Tier → Score, four base-score factors, Bayesian reviews, reliability, and deterministic tiebreakers.

## Open-source and synchronization commitment

This specification is published under the MIT License. It is the approved implementation target for launch. Once the algorithm is implemented, a change to a gate, tier, factor, weight, formula, threshold, multiplier, or tiebreaker requires a paired public-specification update in the same release window.

