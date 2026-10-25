# Delayed Divergence

## A reproducible evidence audit of the Moderna–Merck mRNA melanoma vaccine and its market reaction

---

## Abstract

**Importance.** The public debate around individualized mRNA cancer vaccines has been shaped by a small number of dramatic claims: that a Phase 3 trial proved a vaccine “works,” that the effect mirrors earlier Phase 2 results, that the vaccine is approved, and that a sharp stock decline revealed bad data. These claims mix clinical evidence, regulatory status, corporate finance, and price action.

**Objective.** To determine which factual propositions in a viral Arabic-language narrative about Moderna, Merck, and intismeran autogene are supported by primary evidence, which are partially supported, and which fail; and to quantify the clinical and market effects without conflating them.

**Design.** A clean-room evidence audit with a 42-claim ledger, a single-firm event study, a Phase 2-to-Phase 3 effect-size comparison, and a financial/valuation reconstruction. Sources were snapshotted byte-for-byte with SHA-256 manifests. The event study uses a market model estimated over 2025-08-01 to 2026-07-31, with SPY as the primary benchmark, XBI and IBB for robustness, 10,000 placebo draws, and abnormal-volume diagnostics.

**Results.** INTerpath-001 randomized 1,137 patients with resected stage IIB–IV melanoma. At a median follow-up of 24.6 months, RFS HR was 0.58 (95% CI 0.45–0.75; p<0.001) and DMFS HR was 0.62 (0.45–0.85; p=0.002). Two-year RFS was 82.2% vs 70.0%; two-year DMFS was 88.5% vs 80.2%. Overall survival remained immature (HR 0.77; 0.45–1.31; p=.33). The benefit was concentrated after six months: first-six-month RFS HR 0.99 (0.66–1.49), post-six-month piecewise HR 0.42 (0.30–0.58). Phase 2 effects attenuated in Phase 3: RFS reduction fell from 49% to 42%, and DMFS reduction from 59% to 38%. On 2026-08-19, MRNA rose 176.97% close-to-close, adding about $44.5B in market value. On 2026-10-22, MRNA fell 17.57% close-to-close and about 25.1% intraday high-to-low despite positive full data. The claim ledger grades 18 claims supported, 14 partially supported, and 10 unsupported.

**Conclusions.** The narrative is directionally right about a positive Phase 3 result and wrong about several vivid details. The scientifically important story is not simply “the vaccine works,” but *when* the benefit appears and *how much* of the Phase 2 effect survived Phase 3. The market story is that price reaction is not an efficacy endpoint. The October selloff is best interpreted as a disclosure and expectations shock, not as evidence of negative efficacy.

---

## 1. Introduction

The development of individualized neoantigen therapy has been one of the most closely watched translational programs in oncology. The idea is conceptually simple: sequence a patient’s tumor, identify mutations that generate neoantigens, manufacture a patient-specific mRNA construct, and combine it with an immune checkpoint inhibitor to train the immune system to recognize residual disease. The clinical and commercial stakes are large, and the public narrative has become correspondingly exaggerated.

This paper audits one such narrative. The source is a viral Arabic-language transcript that presents a set of claims about Moderna, Merck, the Phase 3 INTerpath-001 trial, the FDA, HHS, and the stock market. Rather than treating the transcript as a single truth claim, we decompose it into 42 testable propositions. We then ask three questions:

1. **Clinical:** What did the trial actually show, and what did it not show?
2. **Temporal:** Is the treatment effect constant, or is it concentrated in a particular period?
3. **Market:** What information events moved the stock, and what can those moves tell us about the data?

The distinction between *supported* and *true* is central. A claim can be supported by a source and still be scientifically contestable. A company press release is excellent evidence for what the company said and weaker evidence for whether the underlying mechanism is correct. An official statement is evidence of official position, not proof of scientific fact. The ledger is designed to make these distinctions explicit.

The paper makes four contributions. First, it provides a claim-level audit with committed source snapshots and reproducible verdicts. Second, it documents a **delayed divergence** in the Phase 3 hazard ratios: the first six months are compatible with no benefit, while the post-six-month period shows a large benefit. Third, it quantifies the Phase 2-to-Phase 3 attenuation, which is larger for DMFS than for RFS. Fourth, it separates the two market events and shows that the October decline is not evidence of negative efficacy.

---

## 2. Evidence base

### 2.1 Sources

The repository contains 29 sources and 28 committed snapshots. The difference is deliberate: one source (a Bloomberg article on short-seller losses) is paywalled and could not be snapshotted; it is retained as a secondary source with a provenance flag. The manifest records SHA-256 hashes, byte sizes, source IDs, publishers, and URLs.

The primary clinical sources are:

- the Merck/Moderna topline release of 2026-08-19 [1];
- the Merck/Moderna detailed Phase 3 release of 2026-10-22 [2];
- the Moderna mirror of the topline release [3];
- ClinicalTrials.gov NCT05933577 [7];
- the ASCO 2026 KEYNOTE-942 5-year abstract [8];
- FDA MFLUSIVA product and clinical-review documents [9];
- HHS BARDA wind-down release [10];
- NIH and Moderna accounts of the 2020 vaccine timeline [11, 23].

The financial sources are Moderna’s 2025 Form 10-K, 2022 Form 10-K product-sales table, and Q2 2026 release [12–14], plus Merck’s 2025 Form 10-K, 2016 collaboration release, 2022 option-exercise release, and 2022 Q4 results [15–18].

The market data are daily prices and volumes for MRNA, MRK, SPY, XBI, and IBB, retrieved from Yahoo Finance and Nasdaq [22]. The event-study methodology is informed by the Federal Reserve’s 2026 placebo study [19]. The claim-ledger design is informed by MIRROR [20].

### 2.2 Why snapshots matter

Live web sources change. A press release can be edited; a PDF can be replaced; a page can disappear. The repository therefore commits the retrieved bytes and hashes them. The verifier recomputes the hashes and fails if the artifact no longer matches the manifest.

The FDA clinical review illustrates the problem. The live PDF endpoint returned HTTP 401 during retrieval. The Internet Archive copy was available, and that copy is committed together with extracted text. The archived provenance is visible in the manifest and in the repository’s methods. This is not a hidden workaround; it is a documented constraint.

---

## 3. Methods

### 3.1 Claim ledger

Each claim is represented as a structured record with:

- a claim ID and category;
- a short paraphrase of the transcript’s proposition;
- a verdict;
- an evidence note;
- one or more source IDs;
- a confidence grade where appropriate.

The verdicts are:

- **supported** — directly supported by a primary or high-quality secondary source;
- **partially supported** — directionally right but wrong in number, timing, scope, or causal interpretation;
- **unsupported** — contradicted by evidence, or asserting something for which no adequate evidence exists;
- **not verifiable** — cannot be tested with available public evidence.

The ledger is not a fact-check of every sentence in the transcript. It is a test of the propositions that carry the narrative’s argumentative weight.

### 3.2 Clinical derivations

We treat reported hazard ratios and rates as inputs, not re-estimates. The derived quantities are arithmetic translations:

- absolute RFS gain = 82.2 − 70.0 = 12.2 percentage points;
- NNT for 2-year RFS = 100/12.2 = 8.20;
- absolute DMFS gain = 88.5 − 80.2 = 8.3 points;
- NNT for 2-year DMFS = 100/8.3 = 12.05;
- delayed-effect ratio = 0.42/0.99 = 0.424;
- post-six-month HR is 57.6% lower than the first-six-month HR;
- Phase 2-to-Phase 3 RFS attenuation = 49 − 42 = 7 percentage points;
- Phase 2-to-Phase 3 DMFS attenuation = 59 − 38 = 21 percentage points;
- any-TRAE excess = 95.8 − 90.0 = 5.8 points; NNH = 17.24;
- Grade 3–5 TRAE excess = 14.2 − 13.4 = 0.8 points; NNH = 125.

These are descriptive. They do not adjust for censoring, competing risks, or baseline covariates.

### 3.3 Event study

We compute daily log returns. The primary model is a one-factor market model:

\[
R_{i,t} = \alpha_i + \beta_i R_{m,t} + \varepsilon_{i,t}
\]

estimated by OLS over 2025-08-01 to 2026-07-31. Abnormal returns are:

\[
\widehat{AR}_{i,t} = R_{i,t} - (\hat\alpha_i + \hat\beta_i R_{m,t})
\]

Cumulative abnormal returns sum AR over the event window. We report:

- raw returns;
- market-model CARs with SPY;
- simple market-adjusted returns;
- market-model and market-adjusted CARs with XBI and IBB.

Using the same estimation window for both events avoids contaminating the model with the first shock. The trade-off is that the estimation window ends before the first event and therefore does not use the most recent pre-event covariance structure. A rolling 120-day robustness check is included in the repository.

### 3.4 Placebo inference

For each event/model/window, we draw 10,000 pseudo-event dates from trading days whose windows do not overlap either real event or a ±10-day guard band. The empirical two-sided p-value is:

\[
p = \frac{1 + \#\{|CAR_{placebo}| \ge |CAR_{event}|\}}{1 + N}
\]

With 10,000 draws, the smallest reportable p-value is 0.0001. A p-value at that floor means that no placebo draw was as extreme as the event; it is not a continuous estimate of “p = 0.0001.”

The placebo design addresses a simple problem: a single event has no sampling distribution. The cross-section of pseudo-events provides a reference distribution under the null that the event date is not special, conditional on the return process.

### 3.5 Volume and valuation

Abnormal volume is event-day volume divided by the median volume over the prior 60 trading days. We also report the log deviation and the prior percentile. This is descriptive, not a structural model of informed trading.

Market capitalization is close × shares outstanding. For the 2026 events, we use 399,235,889 shares as of 2026-07-24. For the 2021 peak, we use 403.6M shares contemporaneous with the peak, because using today’s share count would understate the historical market value. Market cap is not enterprise value; it ignores debt, cash, and dilution.

### 3.6 Reproducibility

The pipeline is deterministic given the committed inputs and a fixed random seed. It writes:

- `data/processed/prices.csv`, `returns.csv`, `event_study.csv`;
- `results/tables/*.csv`;
- `results/figures/*.png` and `paper/figures/*.png`;
- `paper/results_summary.json`;
- updated manifests.

`python scripts/verify.py` checks manifest integrity and key numerical invariants. `make all` runs the pipeline, tests, and verifier. The containerized reproduction uses `docker compose run --rm lab make all`.

---

## 4. Results

### 4.1 Trial design and primary results

INTerpath-001 is a randomized, double-blind Phase 3 trial in patients with completely resected stage IIB–IV melanoma. Patients were randomized 2:1 to intismeran autogene plus pembrolizumab or placebo plus pembrolizumab. The trial randomized 1,137 patients: 757 in the combination arm and 380 in the control arm. Safety analyses used 755 and 380 patients, respectively, for a total of 1,135.

At a median follow-up of 24.6 months:

| Endpoint | Combination | Control | Effect |
|---|---:|---:|---|
| 2-year RFS | 82.2% (79.3–84.8) | 70.0% (65.0–74.5) | HR 0.58 (0.45–0.75), p<0.001 |
| 2-year DMFS | 88.5% (86.0–90.6) | 80.2% (75.6–84.0) | HR 0.62 (0.45–0.85), p=0.002 |
| OS | immature | immature | HR 0.77 (0.45–1.31), p=.33 |

The primary endpoint was met. The key secondary endpoint, DMFS, was also met. Overall survival was not statistically significant and remains immature.

The absolute benefit is clinically meaningful but smaller than the relative reduction suggests. The 2-year RFS gain is 12.2 percentage points, or one additional recurrence-free patient for every 8.2 treated. The 2-year DMFS gain is 8.3 points, or one additional distant-metastasis-free patient for every 12.0 treated. These numbers are useful because they translate relative hazards into a scale that patients and clinicians can interpret.

### 4.2 Delayed divergence

The average hazard ratio conceals a sharp time dependence. The first six months show no separation:

- RFS HR 0.99 (0.66–1.49);
- DMFS HR 1.01 (0.58–1.79).

After six months, the piecewise hazard ratios are:

- RFS HR 0.42 (0.30–0.58);
- DMFS HR 0.50 (0.34–0.73).

The post-six-month RFS hazard ratio is 57.6% lower than the first-six-month hazard ratio (0.42/0.99 = 0.424). The pattern is consistent with a delayed adaptive immune response, but the trial was not designed to prove mechanism. The defensible statement is that **the benefit is time-dependent in the observed data**, not that the vaccine mechanically cannot work before six months.

This pattern matters for interpretation. A reader who sees only the overall HR of 0.58 may imagine a constant benefit. A reader who sees only the first-six-month HR of 0.99 may conclude the vaccine does not work. Neither reading is adequate. The data show a delayed divergence: early convergence, later separation.

### 4.3 Phase 2-to-Phase 3 attenuation

The 5-year KEYNOTE-942 update reported a 49% RFS reduction (HR 0.51; 0.29–0.89) and a 59% DMFS reduction (HR 0.41; 0.20–0.84) in 157 patients. Phase 3 attenuated both effects:

| Comparison | Phase 2 | Phase 3 | Attenuation |
|---|---:|---:|---:|
| RFS reduction | 49% | 42% | 7 pp (14.3% relative) |
| DMFS reduction | 59% | 38% | 21 pp (35.6% relative) |
| RFS HR | 0.51 | 0.58 | ratio 1.14 |
| DMFS HR | 0.41 | 0.62 | ratio 1.51 |

This is the pattern expected from winner’s curse and effect-size shrinkage when a promising Phase 2 moves to a larger, more definitive trial. It does not make the Phase 3 result negative. It does mean that quoting the Phase 2 number as if it were the confirmed effect is misleading.

The mITT sensitivity analysis is also relevant. In the mITT population, RFS HR was 0.51 (0.39–0.67) and DMFS HR was 0.55 (0.40–0.77), both more favorable than the ITT estimates. The difference between mITT and ITT is modest for RFS (ratio 0.88) and larger for DMFS. This is a reminder that “the” hazard ratio depends on the population and analysis set.

### 4.4 Safety

Safety was reported for 755 combination and 380 control patients:

- any TRAE: 95.8% vs 90.0%;
- Grade 3–5 TRAE: 14.2% vs 13.4%;
- common events: pyrexia 52.2%, injection-site pain 51.0%, fatigue 38.5%.

The any-TRAE excess is 5.8 percentage points, or one additional any-grade TRAE for every 17.2 treated. The Grade 3–5 excess is 0.8 points, or one additional Grade 3–5 TRAE for every 125 treated. The latter is imprecise but reassuring in magnitude; the former is consistent with the expected reactogenicity of an mRNA vaccine.

### 4.5 Market events

#### Event 1: 2026-08-19 topline

| Window | Raw return | Market-model CAR (SPY) | Placebo p |
|---|---:|---:|---:|
| [0,0] | +176.97% | +175.66% | 0.0001 |
| [−1,1] | +106.83% | +110.31% | 0.0001 |
| [0,1] | +111.75% | +113.31% | 0.0001 |
| [0,5] | +137.71% | +136.39% | 0.0001 |
| [0,20] | +151.06% | +146.27% | 0.0001 |

The XBI-adjusted event-day CAR was +155.29% (p=0.0001), and the [−1,1] CAR was +100.25% (p=0.0001). The market-model beta versus SPY was 1.593 (R²=0.092); versus XBI it was 1.434 (R²=0.322). The low R² versus SPY is important: most of MRNA’s daily variance is idiosyncratic, so the abnormal return is large but the model explains little of the total variance.

Volume was 199.25M shares, or 33.5× the prior 60-day median. Dollar volume was about $34.75B. The event-day close was $174.38, up from $62.96, adding about $44.48B in market value. Intraday, the stock traded between $114.46 and $176.66.

#### Event 2: 2026-10-22 detailed data and leak

| Window | Raw return | Market-model CAR (SPY) | Placebo p |
|---|---:|---:|---:|
| [0,0] | −17.57% | −16.11% | 0.0026 |
| [−1,1] | −17.34% | −16.12% | 0.0214 |
| [0,1] | −18.60% | −16.58% | 0.0119 |
| [0,5] | not estimable | not estimable | — |
| [0,20] | not estimable | not estimable | — |

The XBI-adjusted event-day CAR was −16.62% (p=0.0001), the [−1,1] CAR was −14.23% (p=0.0261), and the [0,1] CAR was −15.95% (p=0.0001). The event-day close was $202.63, down from $245.81, destroying about $17.24B in market value. Intraday, the stock traded between $180.80 and $241.264, a high-to-low decline of 25.06%.

The full data released later that day were positive. CNBC reported that the stock fell “even though the full data, released later Thursday, appeared positive” [4]. UBS analysts called it “overall a strong data set” and attributed the reaction to “massive expectations” rather than disappointing data [4]. The correct interpretation is a disclosure and expectations shock, not negative efficacy.

#### Benchmark spillovers

On 2026-08-19, MRK rose 12.6%, XBI rose 5.9%, and SPY rose 0.21%. On 2026-10-22, MRK fell 1.76%, XBI fell 0.75%, and SPY fell 1.18%. The August event had sector spillover; the October event was more idiosyncratic. This is consistent with the August news being a class-level proof of concept and the October news being a firm-specific expectations reset.

### 4.6 Valuation and long-run performance

Using 399,235,889 shares:

| Date | Close | Market cap | Change |
|---|---:|---:|---:|
| 2026-08-18 | $62.96 | $25.14B | — |
| 2026-08-19 | $174.38 | $69.62B | +$44.48B |
| 2026-10-21 | $245.81 | $98.14B | — |
| 2026-10-22 | $202.63 | $80.90B | −$17.24B |

The long-run history corrects several impressionistic claims:

- peak close $484.47 on 2021-08-09;
- post-peak closing trough $22.36 on 2025-11-20;
- maximum close-to-close drawdown −95.38%;
- annual returns: 2023 −44.63%, 2024 −58.19%, 2025 −29.08%;
- 2026 YTD through 2026-10-22: +587.1%.

The transcript’s “lost two-thirds in 2023” is false: 2023 was −44.63%, and the two-thirds-scale decline was 2024 (−58.19%). The “stock fell below $10” claim is also false: the closing trough was $22.36. The “market cap above $200B” claim is partially supported: the peak close implies about $195.6B, while the intraday peak implies about $200.8B using contemporaneous shares.

### 4.7 Financial reconstruction

| Year | Revenue | Product sales | Net income | R&D |
|---|---:|---:|---:|---:|
| 2021 | $18.471B | $17.675B | $12.202B | $1.991B |
| 2022 | $19.263B | $18.435B | $8.362B | $3.295B |
| 2023 | $6.848B | $6.671B | −$4.714B | $4.845B |
| 2024 | $3.236B | $3.109B | −$3.561B | $4.543B |
| 2025 | $1.944B | $1.818B | −$2.822B | $3.132B |

Pandemic-era revenue was $37.734B across 2021–2022, with product sales of $36.110B. The post-pandemic decline was multi-year. The $3B-scale revenue year was 2024, not 2023. Q2 2026 revenue was $145M, with a $782M net loss, a $1.97 EPS loss, and $651M of R&D.

Keytruda was $20.937B of Merck’s $59.283B 2022 revenue, or 35.3%. That supports the “about one-third” claim for 2022, but not as a permanent structural fact. Merck’s 2025 10-K states that the core compound patent expires in December 2028, with two additional patents extending into 2029 due to patent term adjustment. The transcript’s “patent expires in 2028” is therefore partially supported: the core patent does, but the exclusivity picture is more complicated.

### 4.8 Claim audit

| Category | Supported | Partially supported | Unsupported |
|---|---:|---:|---:|
| Clinical | 7 | 4 | 2 |
| Corporate | 1 | 3 | 0 |
| Financial | 2 | 1 | 0 |
| Manufacturing | 1 | 0 | 0 |
| Market | 2 | 4 | 5 |
| Policy | 2 | 0 | 0 |
| Publication | 0 | 1 | 0 |
| Regulatory | 1 | 0 | 2 |
| Science | 1 | 0 | 1 |
| Valuation | 1 | 1 | 0 |
| **Total** | **18** | **14** | **10** |

The market category contains the most unsupported claims. This is not because market data are unavailable, but because the transcript uses price action as evidence about efficacy. The clinical category is mostly supported or partially supported: the transcript gets the direction right but overstates certainty and understates time dependence.

Two grading nuances deserve emphasis. First, C21 (HHS’s assertion that mRNA vaccines “fail to protect effectively”) is graded **supported** because HHS said it, not because the assertion is scientifically correct. Second, C31 (short sellers lost $5.5B) is graded **partially supported** because the estimate is proprietary and cannot be independently reproduced from public data.

---

## 5. Discussion

### 5.1 What the trial shows

The trial shows a statistically significant improvement in RFS and DMFS for an individualized mRNA neoantigen therapy combined with pembrolizumab in resected high-risk melanoma. The effect is clinically meaningful: a 12.2-point absolute RFS gain at two years and an NNT of about 8. The DMFS gain is smaller in absolute terms (8.3 points; NNT about 12), but the relative reduction is still substantial.

The trial does not show an overall survival benefit. The OS hazard ratio of 0.77 is encouraging but imprecise; the confidence interval includes no effect. The appropriate statement is that OS data are immature, not that the vaccine “extends survival.”

The trial also does not show that the vaccine prevents melanoma. It is an adjuvant treatment for patients with resected disease. Conflating adjuvant treatment with prevention is a category error.

### 5.2 Why delayed divergence matters

The first-six-month hazard ratio of 0.99 is not a failure. It is a description of the early period. The post-six-month hazard ratio of 0.42 is not a separate trial. It is a piecewise estimate from the same trial. The overall hazard ratio of 0.58 is a weighted average of these periods.

This pattern has at least three implications.

First, it changes the interpretation of the absolute benefit. A patient who is recurrence-free at six months has a different conditional prognosis than a patient at time zero. The 12.2-point absolute gain is an average over the whole two-year period, not a constant per-month effect.

Second, it changes the interpretation of the Phase 2 comparison. The Phase 2 5-year data showed a large effect, but the Phase 3 effect is attenuated. The attenuation is larger for DMFS than for RFS. This is consistent with the Phase 2 DMFS estimate being especially fragile.

Third, it changes the market interpretation. A reader who sees the first-six-month HR of 0.99 might think the detailed data were negative. A reader who sees the post-six-month HR of 0.42 might think the data were overwhelmingly positive. Both readings are incomplete. The market’s initial reaction appears to have focused on the early-period data and the disappointment relative to expectations; the full data were more favorable.

### 5.3 Why the market reaction is not an endpoint

The August event was a genuine surprise: a Phase 3 trial in a high-risk adjuvant setting met its primary endpoint, and the stock repriced by 177% in one day. The October event was a different kind of surprise: the full data were positive, but the disclosure sequence and the early-period hazard ratios disappointed expectations. The stock fell 17.6% close-to-close and 25.1% intraday.

Neither move tells us whether the vaccine works. The August move tells us the market updated positively on the topline. The October move tells us the market updated negatively on the disclosure and the details relative to expectations. The clinical endpoint is RFS/DMFS/OS, not the stock price.

This is not a claim that markets are irrational. It is a claim that price is a noisy, forward-looking, expectations-weighted signal. A 177% move is evidence of a large update, not evidence of a 177% clinical effect. A 17.6% decline is evidence of a large negative update, not evidence of negative efficacy.

### 5.4 What the transcript gets right and wrong

The transcript gets several important things right:

- the trial met its primary endpoint;
- the relative RFS reduction was 42%;
- the 2-year RFS rates were 82% vs 70%;
- the benefit was larger after six months;
- the August topline produced a massive positive market reaction;
- Moderna’s pandemic revenue was enormous;
- HHS announced a wind-down of mRNA projects;
- Keytruda was about one-third of Merck’s 2022 revenue.

It gets several things wrong or partially wrong:

- it treats the vaccine as approved;
- it treats the trial as proving survival benefit;
- it treats the October drop as evidence of bad data;
- it says Moderna lost two-thirds in 2023 (actually 2024);
- it says 2023 revenue was $3B (actually 2024);
- it says the stock fell below $10 (trough was $22.36);
- it says the market cap exceeded $200B (only intraday, barely);
- it says about 4,500 employees (about 4,700);
- it says $500M was canceled (HHS says nearly $500M);
- it says the flu vaccine is “27% stronger” (26.6% relative efficacy overall; 27.4% in ≥65; not absolute).

The pattern is not random. The transcript is strongest on the broad clinical direction and weakest on precise numbers, timing, and causal interpretation. That is exactly the pattern a claim ledger is designed to expose.

---

## 6. Limitations

1. **Single-firm event study.** MRNA is volatile and idiosyncratic. The market model explains only about 9% of daily variance versus SPY and 32% versus XBI. Placebo inference is robust to non-normality but cannot rule out all omitted news.
2. **Event-date ambiguity.** The October event involved a leak and a later full release. Daily data cannot resolve intraday headline sequencing or analyst revisions.
3. **Surrogate endpoints.** RFS and DMFS are not overall survival. The OS confidence interval is wide and compatible with substantial benefit or no benefit.
4. **Publication status.** The Phase 3 results were presented at ESMO 2026 as LBA1 and accepted by NEJM, but no DOI or published version was available as of 2026-10-24. This paper does not call them peer-reviewed published.
5. **Registry lag.** ClinicalTrials.gov still listed an estimated enrollment of 1,089 while the companies reported 1,137 randomized. The registry is useful for design and dates, not for final enrollment.
6. **Safety denominators.** Safety analyses used 1,135 patients, not 1,137 randomized. The difference is small but should not be hidden.
7. **Proprietary short-interest data.** The $5.5B short-seller loss is a Bloomberg/S3 estimate, not independently reproducible from public data.
8. **Official statements are not truth.** HHS’s assertion that mRNA vaccines “fail to protect effectively” is recorded as an official claim, not endorsed as a scientific conclusion. The evidence is product-specific and contested.
9. **Market-cap precision.** Close × current shares is not enterprise value. The “$200B” claim is reproducible only on an intraday peak with contemporaneous shares.
10. **No causal claim about mechanism.** The delayed hazard pattern is an observed statistical pattern. The paper does not prove that the six-month immunization schedule causes the delay.

---

## 7. Reproducibility and data availability

The repository is self-contained. The committed snapshots and price files allow offline reproduction. The pipeline is deterministic given the fixed seed.

```bash
pip install -e ".[dev]"
make all
```

The verifier checks manifest hashes and key numerical invariants. The containerized reproduction is:

```bash
docker compose run --rm lab make all
```

The generated manuscript inputs are in `paper/results_summary.json`. The full claim ledger is in `results/tables/claims.csv`. The source ledger is in `results/tables/sources.csv`.

---

## References

1. Merck & Co. and Moderna. Merck and Moderna Announce Phase 3 INTerpath-001 Trial of Intismeran Autogene Plus KEYTRUDA Met Endpoints of Recurrence-Free Survival (RFS) and Distant Metastasis-Free Survival (DMFS) in Patients With Completely Resected Stage IIB-IV Melanoma. 2026-08-19.
2. Merck & Co. and Moderna. Merck and Moderna Will Present Results From Landmark Phase 3 INTerpath-001 Trial for Intismeran Autogene Plus KEYTRUDA (pembrolizumab) at ESMO 2026 Presidential Symposium. 2026-10-22.
3. Moderna. Merck and Moderna Announce Phase 3 INTerpath-001 Trial Met Endpoints. 2026-08-19.
4. Constantino AK, Pramuk J. Moderna shares plunge after cancer vaccine data leaks — despite positive results. CNBC. 2026-10-22.
5. Science Media Centre. Expert reaction to abstract of Phase 3 INTerpath-001 trial results of an individualised mRNA vaccine for resected stage IIB-IV melanoma. 2026-10-23.
6. OncLive. Adjuvant Intismeran Autogene Plus Pembrolizumab Improves RFS and DMFS in Melanoma. 2026-10-22.
7. ClinicalTrials.gov. NCT05933577: A Study of Intismeran Autogene (V940) in Combination With Pembrolizumab Versus Placebo in Participants With Resected Melanoma. 2026.
8. Journal of Clinical Oncology. Individualized neoantigen therapy intismeran autogene plus pembrolizumab in resected melanoma: 5-year update of KEYNOTE-942. DOI 10.1200/JCO.2026.44.16_suppl.9500.
9. U.S. Food and Drug Administration. MFLUSIVA product page and clinical review. 2026.
10. U.S. Department of Health and Human Services. HHS Winds Down mRNA Vaccine Development Under BARDA. 2025-08-05.
11. NIH Intramural Research Program. That Record-breaking Sprint to Create a COVID-19 Vaccine. 2021.
12. Moderna, Inc. Form 10-K for fiscal year 2025.
13. Moderna, Inc. 2022 Form 10-K product-sales table.
14. Moderna, Inc. Second-quarter 2026 results.
15. Merck & Co. Form 10-K for fiscal year 2025.
16. Merck & Co. Merck and Moderna Announce Strategic Collaboration on mRNA-Based Personalized Cancer Vaccines. 2016-06-29.
17. Merck & Co. Merck and Moderna Announce Exercise of Option for Joint Development and Commercialization. 2022-10-12.
18. Merck & Co. Fourth-quarter and full-year 2022 results. 2023-02-02.
19. Coglianese J, Fang JA. An Evaluation of Difference-in-Differences Methods Using Placebo Event Studies. Finance and Economics Discussion Series 2026-045. Federal Reserve Board, 2026. DOI 10.17016/FEDS.2026.045.
20. MIRROR: Local Evidence Bundles for Reproducible Research Software Review, with a JANUS Case Study. Journal of Open Research Software. DOI 10.5334/jors.753.
21. Bloomberg. Moderna’s 160% Surge Burns Shorts in Painful $5 Billion Loss. 2026-08-19. Paywalled; not snapshotted.
22. Yahoo Finance and Nasdaq historical price/volume data. Retrieved 2026-10-24.
23. Moderna, Inc. SEC exhibit on the COVID-19 vaccine timeline. 2020-03-16.

Full URLs and snapshot paths are in `config/sources.yaml` and `results/tables/sources.csv`.
