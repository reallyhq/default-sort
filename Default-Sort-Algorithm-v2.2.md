# Default Sort Algorithm for Provider Search and Navigation (v 2.2)

This specification explains the scoring logic used to rank providers in Really Global’s directory.  
Version 2.2 corrects header names, fixes typos (“availability”, “length”), and removes placeholder columns that previously appeared as “Unnamed: n”.

| # | Benefit | Specific factor | Metric | Weight | Scale | How to calculate | MVP flag |
|---|---------|----------------|--------|--------|-------|------------------|----------|
| 1 | Availability | Number of bookable time‑slots in the next 7 days | Count of open appointment slots | 20 pts | 0 – 20 | `min(total_slots, 20)` | ✓ |
| 2 | Response speed | Time to confirm / reply to booking request | Hours (rounded) | 15 pts | 0 – 15 | `IF hrs≤2 → 15; 2<hrs≤12 → 10; 12<hrs≤24 → 5; else 0` | ✓ |
| 3 | Credentials verified | License or credential status checked by Really | Boolean | 15 pts | 0 / 15 | `15 if verified else 0` | ✓ |
| 4 | Session length options | Choice of 30 / 45 / 60‑min sessions | Count of distinct durations offered | 10 pts | 0 – 10 | `distinct_lengths × 5 (‑‑capped at 10)` |   |
| 5 | Languages supported | Extra client languages besides provider’s native | Count | 10 pts | 0 – 10 | `min(extra_langs, 2)× 5` |   |
| 6 | Client reviews | Average star rating (last 12 m) | 1–5 stars | 10 pts | 0 – 10 | `(avg_stars − 3)× 5`, floor at 0 |   |
| 7 | Talk Now availability | Offers instant, on‑demand sessions | Boolean | 10 pts | 0 / 10 | `10 if true else 0` |   |
| 8 | Sliding‑scale pricing | Offers lower‑cost sliding scale | Boolean | 5 pts | 0 / 5 | `5 if true else 0` |   |
| 9 | Community affiliation | Shares a client’s selected identity / community | Boolean | 5 pts | 0 / 5 | `5 if overlap else 0` |   |

**Total possible score:** 100 points.

> **Gate logic**  
> * Gate 1 – show only providers with ≥ 1 open slot in next 7 days.  
> * Gate 2 – hide providers whose licenses cannot be auto‑verified.  
> * Gate 3 – separate “Verified” vs “Non‑Verified” lists; apply the same sort formula inside each gate.