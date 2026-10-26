# Default Sort Algorithm — Really Global

This repository publishes the rules Really Global uses to order eligible providers in marketplace results. Publishing the rules lets providers, clients, and outside observers understand the order and check whether it is being applied as described.

## Current approved specification

**v3.4, October 2026**

See [Default-Sort-Algorithm-v3.4.md](./Default-Sort-Algorithm-v3.4.md) for the full public specification and [default-sort.csv](./default-sort.csv) for the machine-readable factor table.

Really Global is pre-launch. v3.4 is the approved implementation target; this repository does not claim that Default Sort is already running in production. When implementation begins, the product and public specification must be released and maintained in lockstep.

## Authoritative source and change control

[Default-Sort-Algorithm-v3.4.md](./Default-Sort-Algorithm-v3.4.md) on the `main` branch is the single authoritative published specification for algorithm v3.4. This README and [default-sort.csv](./default-sort.csv) must identify the same current version.

Really Global's internal Confluence BRD is the product-requirements and approval record; it is not a separate public specification. After a change is approved internally, it must be published through a GitHub pull request and merged to `main` before it becomes part of the authoritative published specification. Once the algorithm is implemented, the running code and the published specification must remain in lockstep.

## What Default Sort does

Every marketplace must display results in some order. Without a disclosed rule, the database still creates an accidental and unstable order. Neutrality therefore does not mean randomness. It means that the same published, non-clinical rules apply consistently and that providers cannot buy placement.

Default Sort runs in three stages:

1. **Filter** — shows only otherwise-eligible providers who have a bookable calendar slot within 14 days or Talk Now active.
2. **Tier** — groups visible providers by Verified status and current Talk Now availability.
3. **Score** — orders providers within a tier using five base-score factors. The Talk Now Reliability multiplier applies only when active Talk Now providers are ordered against one another.

The Top Nav "Anyone available now" Talk Now option rings providers in this same order: Verified providers first, then by score, with no separate fairness algorithm and no randomness. Rings from that option count toward a provider's Reliability Score exactly like rings to a named provider.

A user-selected sort changes the order of the providers who pass Stage 1. It does not change who passes Stage 1.

The default sort is identical for every signed-in client and every public visitor. Personalized ordering (preference-based, history-based, or similar) is a separate feature — not part of the default sort.

This does not remove customer filters, customer-selected sorting or separate relevance/matching features.

The five base-score factors are:

- Amount of Availability — 20 points
- Professional Preparation: Experience — 20 points
- Professional Preparation: Credential Breadth — 20 points
- Client Reviews, Bayesian-weighted — 20 points
- Real-Time Audio Translation Enablement — 10 points

## Principles

- **Ordering, not clinical ranking.** A position is not a claim that one provider is clinically better or right for a particular client.
- **Attributed and operational inputs.** The rules use provider attestations, client ratings, independent verification outcomes, and disclosed service events.
- **No paid placement.** The provider pays the applicable Verification Fee needed to cover the third-party verification and related processing costs. Payment does not guarantee Verified status. If independent verification is successfully completed, the resulting Verified status affects the Company’s default tier. Except for this disclosed effect of successful verification, no fee paid to Really Global affects ranking or purchases placement.
- **Client choice controls.** Filters, user-selected sorts, semantic relevance, explicit matching preferences, and the client's own decision may change or override the default order.
- **Open and versioned.** The published spec and the production system are versioned together. Any change to one requires a change to the other in the same release.

Really Global does not make clinical recommendations or determine which Company is right for you. Search results, filters, ratings, and routing tools support your choice of services; they are not a clinical judgment about a Company.

## Files

- [Default-Sort-Algorithm-v3.4.md](./Default-Sort-Algorithm-v3.4.md): current approved public specification
- [default-sort.csv](./default-sort.csv) — machine-readable factors, gates, tiers, multiplier, and tiebreakers
- [Default-Sort-Algorithm-v3.3.md](./Default-Sort-Algorithm-v3.3.md): prior public specification retained for history
- [Default-Sort-Algorithm-v3.1.md](./Default-Sort-Algorithm-v3.1.md) — prior public specification retained for history
- [LICENSE](./LICENSE) — MIT License

## Version history

- **v3.4, October 2026.** "Anyone available now" fan-out rings count toward the Reliability Score like named-provider rings, and fan-out rings providers in Default Sort order. Verification is described as a paid service performed by Certn. No factor, weight, or point value changes.
- **v3.3 — August 2026.** Adds the approved Credential Breadth formula and corrected Talk Now-local Reliability model; aligns experience coverage, Review System inputs, 97-language context, and pre-launch status.
- **v3.1 — May 2026.** Added Real-Time Audio Translation Enablement as the fifth base-score factor.
- **v3.0 — April 2026.** Initial Filter → Tier → Score public architecture.

## Help Center

At launch, the plain-language Help Center page “How Default Sort Works”, reached from the “Why this order?” link on search results, will link here and will be available through Really Global's standard 97-language publication process.

## Questions or discrepancies

If the running product differs from the current public specification after implementation, or if a rule is unclear, please open an issue in this repository.

## License

MIT License. See [LICENSE](./LICENSE).

