# Default Sort Algorithm — Really Global

This repository is the public, open-source specification of the algorithm Really Global uses to order providers in search results. The algorithm is published in full so that providers, clients, and external observers can understand and verify how providers are ranked on the platform.

## Current Version

**v3.1** (May 2026) — adds Real-Time Audio Translation Enablement as a 5th base score factor. Base score range expands from 0–80 to 0–90; maximum effective final score from 88 to 99.

See [`Default-Sort-Algorithm-v3.1.md`](./Default-Sort-Algorithm-v3.1.md) for the full specification.

## What is Default Sort

Default Sort is the algorithm that determines the order of providers when a client browses or searches for mental health providers on Really Global. Given a population of providers (those matching a given URL constraint, e.g. a specific city + specialty page), the algorithm produces an ordered list.

The algorithm runs in three stages:

1. **Filter** — A provider must have a bookable calendar slot in the next 14 days OR have Talk Now (real-time connection) currently active. Providers who fail the filter are not shown.

2. **Tier** — Surviving providers are placed in one of four tiers based on Verified status and Talk Now active status. Tier ordering is fixed: Verified + Talk Now active > Verified + Calendar > Not Verified + Talk Now active > Not Verified + Calendar.

3. **Score** — Within each tier, providers are ranked by `final_score = base_score × reliability_multiplier`, where `base_score` sums five operational factors (max 90) and `reliability_multiplier` reflects the provider's recent operational reliability.

## Files in This Repository

- [`Default-Sort-Algorithm-v3.1.md`](./Default-Sort-Algorithm-v3.1.md) — Full specification of v3.1
- [`default-sort.csv`](./default-sort.csv) — Machine-readable factor table and supporting structure
- [`README.md`](./README.md) — This file
- [`LICENSE`](./LICENSE) — MIT License

## Principles

The algorithm is built on three principles:

- **Operational, not clinical.** Every factor in the algorithm reflects an observable operational fact about the provider (availability, experience, credentials, reviews, capacity to serve cross-language sessions, recent reliability events). The platform makes no claim about the clinical quality of any individual provider's care.

- **Marketplace-neutral.** No provider receives a hidden boost or penalty. There is no preferred-partner status, no advertising-influenced ranking, no editorial promotion. Two providers with identical signals receive identical rankings.

- **Open-source and versioned.** This repository is published under the MIT License. Production code and this specification must remain in sync; CI checks fail if the algorithm code changes without a paired specification update.

## Version Sync Commitment

Really Global commits to keeping the production algorithm and this public specification in lockstep. Any change to the algorithm in production requires a paired update to this repository in the same release window.

## Version History

- **v3.1** (May 2026) — Adds Real-Time Audio Translation Enablement as 5th base score factor (10 points binary, awarded uniformly across all SERPs). Base score range 0–80 → 0–90. Maximum effective score 88 → 99. The v3.0 three-stage architecture, four pre-v3.1 base score factors, Bayesian Reviews formula, Reliability multiplier, tier definitions, and Suspended-not-Platform-suspended distinction are preserved unchanged.

- **v3.0** (April 2026) — Initial public release. Three-stage architecture (Filter → Tier → Score). Four base score factors (Availability, Experience, Credentials, Bayesian-weighted Reviews). Reliability Score multiplier with cold-start handling. Supersedes the unpublished v2.x drafts.

## Help Center

For a plain-language explanation of how providers are ordered, see Really Global's Help Center "Why this order?" page (linked from every search results page, available in all 57 supported languages).

## Questions or Issues

If you believe you've found a discrepancy between this specification and the production algorithm, or have questions about how the algorithm works, please open an issue on this repository.

## License

MIT License. See [`LICENSE`](./LICENSE) for details.
