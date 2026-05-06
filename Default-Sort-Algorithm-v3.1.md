# Default Sort Algorithm — v3.1

**Version:** 3.1
**Date:** May 2026
**Status:** Canonical — supersedes v3.0
**License:** MIT

## Status

This is the canonical specification of Really Global's Default Sort algorithm as of May 2026. v3.1 adds a single new base score factor (Real-Time Audio Translation Enablement) to the v3.0 architecture, which is otherwise preserved unchanged.

This document and the production code are versioned together. Any divergence between the production code and this specification is a bug.

## Overview

Default Sort orders providers in Really Global's search results. Given a population of providers (those matching a URL constraint such as `/en/us/wa/seattle/clinical-social-workers`), the algorithm produces an ordered list.

The algorithm is a three-stage pipeline:

1. **Filter** (Stage 1) — provider must clear a basic availability gate or be excluded from the search results entirely.
2. **Tier** (Stage 2) — surviving providers are assigned to one of four tiers based on Verified status and Talk Now active status.
3. **Score** (Stage 3) — within each tier, providers are ordered by `base_score × reliability_multiplier`, with deterministic tiebreakers.

## Stage 1: Filter

A provider appears in search results only if at least one of the following is true:

- The provider has at least one bookable calendar slot in the next 14 days, OR
- The provider's Talk Now toggle is currently active.

```
visible = has_bookable_slot_in_next_14_days(provider) OR talk_now_toggle_currently_on(provider)
```

Providers who fail this filter are not shown. They are not assigned a tier and not assigned a score.

Rationale: a provider with no upcoming availability and no real-time connection capability cannot be booked. Showing them in search results frustrates clients without serving providers.

## Stage 2: Tier

Surviving providers are assigned to one of four tiers. Tier ordering is fixed: lower-numbered tiers always rank above higher-numbered tiers regardless of within-tier score.

| Tier | Composition |
|------|-------------|
| Tier 1 | Verified + Talk Now active |
| Tier 2 | Verified + Calendar available (Talk Now not active) |
| Tier 3 | Not Verified + Talk Now active |
| Tier 4 | Not Verified + Calendar available (Talk Now not active) |

A Verified provider always ranks above a Not Verified provider. Within each Verified status, a Talk Now active provider always ranks above one without Talk Now active.

**Why Verified dominates Talk Now.** Verification confirms via third-party check that the provider's listed credentials are genuine. Talk Now is a present-tense availability signal. Weighting credentials above availability ensures a non-verified provider cannot shortcut to the top simply by toggling Talk Now on. Verification is voluntary, free, and fast; no path to verification requires payment to the platform.

**Note on "Suspended."** "Suspended" in the Reliability Score sense means Talk Now suspended (the provider's Talk Now toggle is forced off and the Talk Now button is hidden from their profile). It does NOT mean the provider is suspended from the platform. A Talk-Now-suspended provider continues to appear in search results via the calendar-availability path (Tier 2 or Tier 4) and their scheduled-session functionality is unaffected.

## Stage 3: Score

Within each tier, providers are ranked by:

```
final_score = base_score × reliability_multiplier
```

where:

- `base_score` is in the range [0, 90] — the sum of five additive factors.
- `reliability_multiplier` is in {0.70, 0.85, 1.00, 1.10} — depending on the provider's Reliability Score tier.
- `final_score` is therefore in [0, 99].

Higher `final_score` means higher rank within tier.

## The Five Base Score Factors

| # | Factor | Max points | Type |
|---|--------|-----------|------|
| 1 | Amount of Availability | 20 | Continuous |
| 2 | Length of professional experience | 20 | Continuous |
| 3 | Licensed or certified | 20 | Continuous |
| 4 | Client Reviews (Bayesian-weighted) | 20 | Continuous |
| 5 | Real-Time Audio Translation Enablement | 10 | Binary |
| **Total** | | **90** | |

### Factor 1: Amount of Availability (0–20 points)

Counts bookable calendar slots in the next 14 days. A provider with two or more bookable slots in the next 14 days starts at the threshold; each additional slot up to 20 adds value, with diminishing returns past 20 slots.

```python
def availability_points(provider):
    slots = count_bookable_slots_in_next_14_days(provider)
    if slots >= 2:
        raw = 20 + min(slots - 2, 18) * (80 / 18)   # 20 to 100 across 2 to 20 slots
    else:
        raw = 0
    return (raw / 100) * 20                          # normalize to 0-20
```

A provider with zero or one slot in 14 days receives zero points (and may have failed Stage 1 entirely if they also have no Talk Now).

### Factor 2: Length of professional experience (0–20 points)

Different provider types have different career arcs. The tier scales reflect what is meaningful in each profession.

| Provider type | Source field | Tier scale (raw, 0–100) |
|---------------|--------------|-------------------------|
| Licensed | Years in Practice | 0–2 yrs = 50; +10 per tier; cap 100 at 20+ yrs |
| Coach | Completed Coaching Hours | 0–500 hrs = 40; +10 per tier; cap 100 at 3,000+ hrs |
| Mentor | Completed Practice Hours | 0–500 hrs = 40; +10 per tier; cap 100 at 2,000+ hrs |

```python
def experience_points(provider):
    raw = experience_raw_score(provider)             # 0-100 from tier table above
    return (raw / 100) * 20                          # normalize to 0-20
```

The floor (50 for Licensed, 40 for Coach/Mentor) recognizes that any experienced-enough-to-be-listed provider deserves a starting position. The ceiling rewards longer track records without becoming a runaway.

### Factor 3: Licensed or certified (0–20 points)

Counts the licenses and certifications visible on the provider's profile. The first license/certification anchors the score; each additional one adds value with a cap.

```python
def credentials_points(provider):
    n = count_licenses_or_certifications(provider)
    if n == 0:
        raw = 0
    elif n == 1:
        raw = 40
    else:
        raw = min(40 + (n - 1) * 20, 100)            # +20 per additional cert, cap at 100
    return (raw / 100) * 20                          # normalize to 0-20
```

This factor is distinct from the Verified gate. Verified asks "are the listed credentials confirmed real?" while this factor asks "how many credentials does this provider hold?"

### Factor 4: Client Reviews (Bayesian-weighted, 0–20 points)

The Bayesian-weighted rating addresses the cold-start problem honestly. A naive average of star ratings would let a single 5-star review outrank a track record of fifty 4.7-star reviews — obviously wrong. Bayesian shrinkage pulls low-volume providers toward the platform-wide mean and lets high-volume providers' actual ratings dominate.

```python
def reviews_points(provider):
    v = count_published_non_voided_reviews(provider)
    R = mean_published_review_rating(provider)
    m = 5                                            # shrinkage parameter
    C = platform_mean_review_rating()                # recomputed nightly

    if v == 0:
        weighted_rating = C
    else:
        weighted_rating = (v / (v + m)) * R + (m / (v + m)) * C

    return max(0, (weighted_rating - 1) * 5)
```

Worked example, assuming platform mean **C = 4.5**:

| Provider | Reviews (v) | Mean (R) | Weighted | Points |
|----------|-------------|----------|----------|--------|
| Brand new | 0 | n/a | 4.50 | 17.5 |
| One 5-star review | 1 | 5.00 | 4.58 | 17.9 |
| One 1-star review | 1 | 1.00 | 3.92 | 14.6 |
| Fifty 4.7-star reviews | 50 | 4.70 | 4.68 | 18.4 |
| Five 4.0-star reviews | 5 | 4.00 | 4.25 | 16.3 |

**Why m = 5.** Aligns with the platform's existing 5-review threshold for displaying fit-signal distributions. Both use 5 as the "enough data to be meaningful" bar.

**Tech-only and removed reviews are excluded** from both v and R for the provider, and from C platform-wide.

### Factor 5: Real-Time Audio Translation Enablement (10 points binary) — NEW IN v3.1

10 points if the provider has Real-Time Audio Translation enabled on their account; 0 points if not.

```python
def translation_enablement_points(provider):
    return 10 if provider.realtime_audio_translation_enabled else 0
```

**Default-enabled.** Real-Time Audio Translation is enabled by default for all providers at account creation. Providers can opt out via account settings, in which case this factor contributes 0 points. Most accurately framed: declining real-time translation costs 10 points relative to the platform default.

**Awarded uniformly across all SERPs** (native-language and non-native-language alike). The factor reflects provider capacity, not SERP context. A translation-enabled provider gets the 10 points in every SERP they appear in, because the signal reflects their capacity to serve clients across languages regardless of which SERP a particular client is searching.

**Why points and not a tier gate.** A tier gate would force the platform to take a position on whether translation is "better than" or "worse than" native language fluency — a value judgment the platform deliberately avoids. Points-based treatment is structurally analogous to how the algorithm treats calendar availability: more open slots multiplies time-based capacity; translation enablement multiplies language-based capacity. Both are operational, observable; neither implies a quality judgment.

**Why binary, not continuous.** Translation enablement is a binary signal at the provider level — they either have the setting on or off. There is no "more or less" version of this signal at the account level; it is a setting, not a measurement. An activity-based variant (points proportional to translated session count or completion rate) is deferred to post-MVP.

**Operational, not clinical.** This factor is treated identically to how the algorithm treats calendar availability: as observable provider capacity, not as a clinical-quality judgment. The platform makes no claim about whether translated sessions deliver better, worse, or equivalent clinical outcomes compared to native-language sessions. It observes that the provider has activated a setting which expands the population they can serve, and assigns marketplace value accordingly.

## Reliability Score Multiplier

The Reliability Score is a separate operational metric tracking provider operational reliability over a rolling 30-day window. It produces a tier:

| Reliability Tier | Score Range | Multiplier |
|------------------|-------------|------------|
| Trusted | 90–100 | 1.10× |
| Standard | 75–89 | 1.00× |
| On Notice | 60–74 | 0.85× |
| Suspended | <60 | 0.70× |

**Why a multiplier and not a 6th additive factor.** An additive factor with weight 20 would cap reliability's impact at 20 points. A multiplier scales the entire base score. This is intentional: reliability gates the credibility of all other factors. A provider with the best credentials in the world who toggles Talk Now on and does not answer is not delivering on what their profile claims; the multiplier reflects that.

**Cold-start.** Providers with fewer than 5 reliability events default to the Trusted tier (1.10×). The platform does not penalize new providers for absence of operational history.

**Post-suspension recovery.** After a 30-day Talk Now suspension is lifted, the provider's effective multiplier is held at 0.70× for an additional 60 days as a recovery window, after which it reflects their then-current Reliability Score normally.

**Suspension is Talk Now only, not platform suspension.** A Suspended provider in this algorithm is one whose Talk Now access has been suspended for repeated reliability failures. Their Talk Now toggle is forced off. They are not suspended from the platform: they keep their profile, continue to receive scheduled bookings, get paid normally, retain access to all platform features, and still earn Factor 5 (Translation Enablement) points if their account-level translation toggle is on. In sort terms, they fall from Tier 1 to Tier 2 (or Tier 3 to Tier 4) and carry the 0.70× multiplier within that tier.

## Tiebreakers

Within a tier, after `final_score` ordering, ties are broken by:

1. Most recent profile update timestamp — descending (more recently updated first)
2. Provider ID — ascending (deterministic stability)

## End-to-End Pseudocode

```python
def default_sort(provider_population):
    # Stage 1: Filter
    visible = [
        p for p in provider_population
        if has_bookable_slot_in_next_14_days(p) or p.talk_now_toggle_on
    ]

    # Stage 2: Tier
    tiers = {1: [], 2: [], 3: [], 4: []}
    for p in visible:
        if p.verified and p.talk_now_toggle_on:
            tiers[1].append(p)
        elif p.verified:
            tiers[2].append(p)
        elif p.talk_now_toggle_on:
            tiers[3].append(p)
        else:
            tiers[4].append(p)

    # Stage 3: Score and order within tier
    result = []
    for tier_num in [1, 2, 3, 4]:
        tier_providers = tiers[tier_num]
        for p in tier_providers:
            p.base_score = (
                availability_points(p)               # 0-20
                + experience_points(p)               # 0-20
                + credentials_points(p)              # 0-20
                + reviews_points(p)                  # 0-20 (Bayesian-weighted)
                + translation_enablement_points(p)   # 0 or 10 (NEW in v3.1)
            )
            p.final_score = p.base_score * reliability_multiplier(p)

        tier_providers.sort(key=lambda p: (
            -p.final_score,                          # primary: highest score first
            -p.profile_updated_at.timestamp(),       # tiebreaker 1: most recent
            p.provider_id                            # tiebreaker 2: deterministic
        ))
        result.extend(tier_providers)

    return result
```

## End-to-End Worked Example

Provider profile: a Verified Licensed Therapist with Talk Now active, 10 calendar slots in 14 days, 12 years in practice, 2 licenses, 18 reviews averaging 4.6 stars, Trusted reliability tier, and Real-Time Audio Translation enabled (default state).

```
Tier:                        1 (Verified + Talk Now active)

Factor 1 (Availability):     raw = 20 + 8 * (80/18) ≈ 55.6  -> 11.1 pts
Factor 2 (Experience):       Licensed, 12 yrs (4 tiers above floor) raw 90 -> 18.0 pts
Factor 3 (Credentials):      2 licenses -> raw 60 -> 12.0 pts
Factor 4 (Reviews):          v=18, R=4.6, C=4.5 -> weighted 4.58 -> 17.9 pts
Factor 5 (Translation):      enabled (default-on) -> 10.0 pts
Base score:                  11.1 + 18.0 + 12.0 + 17.9 + 10.0 = 69.0 pts

Reliability multiplier:      Trusted (1.10x)
Final score:                 69.0 * 1.10 = 75.9 pts within Tier 1
```

If the same provider had opted out of Real-Time Audio Translation, their final score would be (59.0 × 1.10) = 64.9. The 11-point delta is the v3.1 magnitude calibration discussed below.

## Magnitude Calibration of Factor 5

The 10-point value for translation enablement is calibrated to be meaningful but not dominant. Two illustrations:

**Two otherwise-identical providers, only difference is translation.** Same Verified status, same Talk Now active state, same 80 base from the four pre-v3.1 factors, same Trusted Reliability tier (1.10×). A has translation enabled (the platform default); B has opted out.

- Provider A: base = 80 + 10 = 90; final = 90 × 1.10 = **99**
- Provider B: base = 80 + 0 = 80; final = 80 × 1.10 = **88**

11-point gap. Meaningful but not dominant.

**Translation does not override fundamentals.** A has 70 base from the four pre-v3.1 factors plus translation enabled. B has 80 base from the four pre-v3.1 factors but has opted out of translation. Both Trusted (1.10×).

- Provider A: base = 70 + 10 = 80; final = 80 × 1.10 = **88**
- Provider B: base = 80 + 0 = 80; final = 80 × 1.10 = **88**

They tie. Translation can compensate for non-maxed fundamentals; it does not override them.

## CPOM Posture

Really Global is structured to avoid Corporate Practice of Medicine (CPOM) exposure. The platform does not employ providers, does not direct clinical care, does not interfere with provider scope of practice, and does not make care-quality determinations.

Every factor in this algorithm is operational, not clinical:

- **Amount of Availability** — counting bookable slots
- **Length of professional experience** — counting years or hours from self-reported, profile-attested fields
- **Licensed or certified** — counting credentials issued by other entities (the platform counts third-party determinations; it does not make them)
- **Client Reviews** — aggregating client speech (star ratings clients themselves assigned). The platform sums numbers; it does not interpret care quality.
- **Real-Time Audio Translation Enablement** — reading whether the provider has a setting toggled on. The platform reads a setting; it does not assess whether translated sessions are clinically equivalent to native-language sessions.
- **Reliability Score multiplier** — measuring performance against an operational commitment the provider made. Operationally analogous to how Uber suspends drivers with low pickup rates or DoorDash deactivates couriers with low completion rates; not a clinical determination.
- **Verified gate** — confirming via third-party verification that listed credentials are genuine. The platform confirms documents exist; it does not assess competence.
- **Talk Now sub-tier** — reading the real-time toggle state.

None of these factors require the platform to read into a session, evaluate clinical scope, judge appropriateness of treatment, or assess care quality. The algorithm orders a directory; it does not practice medicine.

## Cold Start

The algorithm does not include a "new provider" boost. Providers without performance data sort according to the same algorithm as everyone else, with cold-start values handled neutrally:

| Factor | Cold start handling |
|--------|---------------------|
| Amount of Availability | Real-time signal; no cold start. New providers populate their calendar during onboarding. |
| Length of professional experience | Self-reported during onboarding; no cold start. |
| Licensed or certified | Self-reported during onboarding; no cold start. |
| Client Reviews (Bayesian) | Bayesian shrinkage handles this directly. v=0 yields the platform mean C — neither favored nor punished. |
| Real-Time Audio Translation Enablement | Default-on at account creation. New providers earn 10 points immediately. No event-count threshold, no warm-up period. Providers who choose to opt out earn 0 points. |
| Reliability Score multiplier | Default Trusted (1.10×) for providers with <5 events. Becomes binding at 5+ events. |

## Deferred Factors

The following factors are deferred to post-MVP iterations:

- **Client Outcomes** (pre/post-test deltas) — deferred pending separate clinical and legal review. Aggregating clinical screening tools into a sort signal moves the platform closer to making care-quality determinations.
- **Response speed**, **Session length options**, **Languages supported (as fluency signal)**, **Sliding-scale pricing**, **Community affiliation** — deferred pending dedicated review.
- **Activity-based variant of translation enablement** — whether the 10-point factor should eventually be tied to actual translated session activity (rather than just the binary toggle state) is deferred. Decision will be informed by empirical data on opt-out rates, gaming behavior, and whether activity-based scoring would penalize new providers in a way that contradicts the cold-start rationale.
- **Magnitude retuning of translation enablement** — the 10-point value is provisional. Empirical data on ranking effects in mature locales may indicate the value should be retuned upward (if the effect is too soft) or downward (if too dominant).
- **Translation-session reliability mechanism** — an auto-off-style mechanism analogous to Talk Now's auto-off triggers, specific to translation-session quality (completion rate, client cancellation, latency thresholds), is post-MVP.
- **Personalization** — Default Sort returns the same order for every user. Personalization is post-MVP.

## Engineering Risks

- **Score recomputation performance.** Several factors are dynamic: availability slot counts change every booking; Talk Now toggle state changes every minute; Reliability Score updates within 60 seconds of every Talk Now event; the platform mean C for Bayesian Reviews recomputes nightly. The score must recompute fast enough to keep search-result renders under target latency. Mitigation: cache Reliability Score and the Bayesian C value; recompute only the per-provider availability factor on each render.
- **Bayesian mean C stability at low volume.** At launch, with very few reviews on the platform, the platform mean C will be unstable. This is acceptable in a known low-data regime; the platform monitors C and may temporarily increase m if C becomes erratic.
- **Reliability Score gaming.** A provider could in principle manipulate their score by toggling off before missing calls. The Talk Now system's auto-off conditions handle most of this. Operational monitoring catches anomalous patterns.
- **Translation enablement gaming.** Once Factor 5 produces sort lift, providers have an incentive to leave translation enabled regardless of preparedness to deliver good translated sessions. In v3.1's binary MVP form, this risk is real but bounded: the value is capped at 10 (out of 90); a provider gaming Factor 5 alone cannot dominate other factors. Translation-session reliability mechanisms are scoped as post-MVP work.
- **Discrepancy between published spec and production code.** The largest risk. Mitigation: a CI check that fails if the spec hasn't been updated when the algorithm code changes. Not a guarantee, but a meaningful tripwire.

## Open-Source Commitment

This specification is published under the MIT License. Production code and this specification must be versioned together. Any change to the algorithm in production requires a paired update to this repository in the same release window. CI gates enforce this.

## Version History

- **v3.1** (May 2026) — Adds Real-Time Audio Translation Enablement as a 5th base score factor (10 points binary, awarded uniformly across all SERPs). Base score range 0–80 → 0–90. Maximum effective score 88 → 99. The v3.0 three-stage architecture, four pre-v3.1 base score factors, Bayesian Reviews formula, Reliability multiplier, tier definitions, and Suspended-not-Platform-suspended distinction are preserved unchanged.
- **v3.0** (April 2026) — Initial public release. Three-stage architecture (Filter → Tier → Score). Four base score factors (Availability, Experience, Credentials, Bayesian-weighted Reviews). Reliability Score multiplier with cold-start handling. Supersedes the unpublished v2.x drafts (which double-counted Verified and lacked the Reliability Score multiplier).

## See Also

- Really Global Help Center page "Why this order?" — plain-language explanation of provider ordering, linked from every search results page, available in 57 languages.
