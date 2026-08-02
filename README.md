# Default Sort Algorithm — Really Global

This repository publishes the rules Really Global uses to order eligible providers in marketplace results. Publishing the rules lets providers, clients, and outside observers understand the order and check whether it is being applied as described.

## Current approved specification

**v3.3 — August 2026**

See [Default-Sort-Algorithm-v3.3.md](./Default-Sort-Algorithm-v3.3.md) for the full public specification and [default-sort.csv](./default-sort.csv) for the machine-readable factor table.

Really Global is pre-launch. v3.3 is the approved implementation target; this repository does not claim that Default Sort is already running in production. When implementation begins, the product and public specification must be released and maintained in lockstep.

## What Default Sort does

Every marketplace must display results in some order. Without a disclosed rule, the database still creates an accidental and unstable order. Neutrality therefore does not mean randomness. It means that the same published, non-clinical rules apply consistently and that providers cannot buy placement.

Default Sort runs in three stages:

1. **Filter** — shows only otherwise-eligible providers who have a bookable calendar slot within 14 days or Talk Now active.
2. **Tier** — groups visible providers by Verified status and current Talk Now availability.
3. **Score** — orders providers within a tier using five base-score factors. The Talk Now Reliability multiplier applies only when active Talk Now providers are ordered against one another.

The five base-score factors are:

- Amount of Availability — 20 points
- Professional Preparation: Experience — 20 points
- Professional Preparation: Credential Breadth — 20 points
- Client Reviews, Bayesian-weighted — 20 points
- Real-Time Audio Translation Enablement — 10 points

## Principles

- **Ordering, not clinical ranking.** A position is not a claim that one provider is clinically better or right for a particular client.
- **Attributed and operational inputs.** The rules use provider attestations, client ratings, independent verification outcomes, and disclosed service events.
- **No paid placement.** A provider cannot buy a score, tier, or position. Paying for verification does not guarantee Verified status and cannot be used to bid for placement.
- **Client choice controls.** Filters, user-selected sorts, semantic relevance, explicit matching preferences, and the client's own decision may change or override the default order.
- **Open and versioned.** Material changes to the running algorithm require a matching update here in the same release window once the algorithm is implemented.

## Files

- [Default-Sort-Algorithm-v3.3.md](./Default-Sort-Algorithm-v3.3.md) — current approved public specification
- [default-sort.csv](./default-sort.csv) — machine-readable factors, gates, tiers, multiplier, and tiebreakers
- [Default-Sort-Algorithm-v3.1.md](./Default-Sort-Algorithm-v3.1.md) — prior public specification retained for history
- [LICENSE](./LICENSE) — MIT License

## Version history

- **v3.3 — August 2026.** Adds the approved Credential Breadth formula and corrected Talk Now-local Reliability model; aligns experience coverage, Review System inputs, 97-language context, and pre-launch status.
- **v3.1 — May 2026.** Added Real-Time Audio Translation Enablement as the fifth base-score factor.
- **v3.0 — April 2026.** Initial Filter → Tier → Score public architecture.

## Help Center

At launch, a plain-language “Why this order?” page will link here and will be available through Really Global's standard 97-language publication process.

## Questions or discrepancies

If the running product differs from the current public specification after implementation, or if a rule is unclear, please open an issue in this repository.

## License

MIT License. See [LICENSE](./LICENSE).

