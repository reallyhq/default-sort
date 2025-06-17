# default-sort

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Open‑source, Excel‑backed algorithm that ranks care providers (0 – 100 pts) by live availability, response speed, credential verification, reviews, and other client‑centric factors.**

---

## Table of Contents
1. [Why use it?](#why-use-it)
2. [How it works](#how-it-works)  
   &nbsp;&nbsp;• [Gate logic](#gate-logic)  
   &nbsp;&nbsp;• [Scoring factors](#scoring-factors)
3. [Quick start](#quick-start)
4. [Files in this repo](#files-in-this-repo)
5. [Contributing](#contributing)
6. [License](#license)

---

## Why use it?
* **Transparent.** Every weight, threshold, and formula lives in plain text (Markdown + CSV/XLS).  
* **Drop‑in.** Works in Excel, Google Sheets, or can be imported into code (Python, JS, etc.).  
* **Client‑first.** Prioritises the attributes that matter most to people seeking help—speed, trust, and fit.  
* **Brand‑agnostic.** No company‑specific hard‑coding; adapt weights to your own platform in minutes.

---

## How it works

### Gate logic
| Gate | Rule | Purpose |
|------|------|---------|
| 1 | ≥ 1 bookable slot in next 7 days | Filters out unavailable providers |
| 2 | Auto‑verified license/credential | Ensures baseline trust |
| 3 | Split list into **Verified** vs **Non‑Verified** | Keeps unverified options visible but clearly separated |

After passing the gates, providers are scored (0–100) on nine factors and sorted high‑to‑low within their group.

### Scoring factors

| # | Factor | Max pts |
|---|--------|--------:|
| 1 | Availability (7‑day open slots) | 20 |
| 2 | Response speed (hours) | 15 |
| 3 | Credentials verified | 15 |
| 4 | Session‑length options | 10 |
| 5 | Languages supported | 10 |
| 6 | Client reviews | 10 |
| 7 | Talk Now availability | 10 |
| 8 | Sliding‑scale pricing | 5 |
| 9 | Community affiliation | 5 |
|   | **Total** | **100** |

Formulas for each factor live in **`Default‑Sort‑Algorithm‑v2.2.md`**.

---

## Quick start

| Want to… | Do this |
|----------|---------|
| **Open default‑sort.csv in Excel** | 1) Clone / download repo.<br>2) Open `default-sort.csv`.<br>3) Replace sample data in column A with your provider list; scores populate automatically. |
| **Use in code** | 1) `pip install pandas` (or similar).<br>2) `df = pandas.read_csv("default-sort.csv")`.<br>3) Apply the formulas in `Default-Sort-Algorithm-v2.2.md` or translate them to SQL / pandas. |

---

## Files in this repo
| File | Purpose |
|------|---------|
| `default-sort.csv` | Clean, diff‑friendly data & weights (can be loaded anywhere). |
| `Default‑Sort‑Algorithm‑v2.2.md` | Full spec: gate rules, weight rationale, formula breakdown. |
| (optional) `examples/` | Worked samples or unit‑test fixtures if you add them later. |

---

## Contributing
We love PRs 🎉

1. **Fork** → `git checkout -b feature/my-improvement`  
2. Make your change + add a test / demo row if relevant  
3. `git commit -m "Explain what you changed"`  
4. `git push` and open a **Pull Request**

See `CONTRIBUTING.md` (if present) for coding style and branch conventions.

---

## License
Released under the [MIT License](LICENSE) – free for personal and commercial use. Attribution welcome but not required.
