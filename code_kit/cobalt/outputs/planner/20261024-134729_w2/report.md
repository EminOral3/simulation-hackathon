# Planner report: week 2 (earliest new decision: week 3)

Generated 13:47:57 in 28s. Surrogate `20261024-133733` (heldout log-loss vs base rate in meta). **Screening only: the hand-in runs are LLM runs.**

## Inputs
- Fixed decisions (week <= 2): none
- Budget left: $4.00M
- Surprises observed: none
- Migration overrun: unknown (averaged over on time / few hours / into Monday)
- Scenarios: 13 (no further surprise + random bad/good mixes), 2 reps each; searched 748 single-action and 314 multi-action decisions, 56 final plans.

## No decision (business as usual from here)
goal_1 83.5 · goal_2 83.7 · goal_3 4.44 · goal_3b 125 · P(all goals) 0%

## Best plans (mean over scenarios; worst = lowest scenario utility)
| # | remaining decision(s) | cost | active % | deposits % | rating | CFPB/mo | P(all) | utility | worst |
|---|---|---|---|---|---|---|---|---|---|
| 1 | w6 | everyone | Early pay up to 2 days early [on]; Savings boost on new money only [+0.25 points]<br>w7 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Zero-interest advance up to $500 [on]; Debit card cash back for 4 weeks [1%, up to $5] | $3.30M | 98.3 | 95.1 | 4.53 | 122 | 26% | 0.06 | -3.94 |
| 2 | w6 | everyone | Early pay up to 2 days early [on]; Goodwill credit to a defined group [$5 each]; Savings boost on new money only [+0.25 points]<br>w7 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Zero-interest advance up to $500 [on]; Debit card cash back for 4 weeks [1%, up to $5] | $3.80M | 98.2 | 94.8 | 4.54 | 122 | 23% | -0.07 | -3.02 |
| 3 | w4 | everyone | Early pay up to 2 days early [on]; Debit card cash back for 4 weeks [1%, up to $5]; Savings boost on new money only [+0.25 points]<br>w6 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Zero-interest advance up to $500 [on]; Goodwill credit to a defined group [$5 each] | $3.80M | 97.2 | 95.4 | 4.56 | 121 | 31% | -0.19 | -4.12 |
| 4 | w4 | everyone | Early pay up to 2 days early [on]; Debit card cash back for 4 weeks [1%, up to $5]; Savings boost on new money only [+0.25 points]<br>w6 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Zero-interest advance up to $500 [on] | $3.30M | 97.1 | 95.7 | 4.55 | 122 | 26% | -0.21 | -4.74 |
| 5 | w6 | everyone | Early pay up to 2 days early [on]; Zero-interest advance up to $500 [on]; Savings boost on new money only [+0.25 points]<br>w7 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Free replacement card on request and payment alerts [on]; Debit card cash back for 4 weeks [1%, up to $5] | $3.60M | 98.5 | 94.3 | 4.54 | 124 | 23% | -0.24 | -3.53 |
| 6 | w6 | everyone | Early pay up to 2 days early [on]; Debit card cash back for 4 weeks [1%, up to $5]; Goodwill credit to a defined group [$5 each]<br>w7 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Zero-interest advance up to $500 [on]; Savings boost on new money only [+0.25 points] | $3.80M | 98.3 | 94.5 | 4.54 | 122 | 19% | -0.38 | -2.93 |
| 7 | w6 | everyone | Early pay up to 2 days early [on]; Zero-interest advance up to $500 [on]<br>w7 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Debit card cash back for 4 weeks [1%, up to $5]; Savings boost on new money only [+0.25 points] | $3.30M | 98.7 | 94.3 | 4.54 | 125 | 11% | -0.41 | -2.48 |
| 8 | w6 | everyone | Early pay up to 2 days early [on]; Zero-interest advance up to $500 [on]; Goodwill credit to a defined group [$5 each]<br>w7 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Debit card cash back for 4 weeks [1%, up to $5]; Savings boost on new money only [+0.25 points] | $3.80M | 98.6 | 94.2 | 4.55 | 122 | 17% | -0.47 | -2.16 |
| 9 | w4 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Early pay up to 2 days early [on]; Savings boost on new money only [+0.25 points]<br>w6 | everyone | Zero-interest advance up to $500 [on]; Debit card cash back for 4 weeks [1%, up to $5]; Goodwill credit to a defined group [$5 each] | $3.80M | 97.2 | 94.5 | 4.55 | 122 | 17% | -0.65 | -3.53 |
| 10 | w5 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Early pay up to 2 days early [on]; Instant dispute credit up to $100 per customer [on]<br>w6 | everyone | Zero-interest advance up to $500 [on]; Debit card cash back for 4 weeks [1%, up to $5]; Goodwill credit to a defined group [$5 each] | $3.80M | 98.0 | 94.2 | 4.56 | 121 | 14% | -0.70 | -2.67 |

## When to act: best plan whose next decision starts in week w
| week | best plan | utility | P(all) |
|---|---|---|---|
| 4 | w4 | everyone | Early pay up to 2 days early [on]; Debit card cash back for 4 weeks [1%, up to $5]; Savings boost on new money only [+0.25 points]<br>w6 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Zero-interest advance up to $500 [on]; Goodwill credit to a defined group [$5 each] | -0.19 | 31% |
| 5 | w5 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Early pay up to 2 days early [on]; Instant dispute credit up to $100 per customer [on]<br>w6 | everyone | Zero-interest advance up to $500 [on]; Debit card cash back for 4 weeks [1%, up to $5]; Goodwill credit to a defined group [$5 each] | -0.70 | 14% |
| 6 | w6 | everyone | Early pay up to 2 days early [on]; Savings boost on new money only [+0.25 points]<br>w7 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Zero-interest advance up to $500 [on]; Debit card cash back for 4 weeks [1%, up to $5] | 0.06 | 26% |

## Top plan per scenario
| scenario | active % | deposits % | rating | CFPB | all goals |
|---|---|---|---|---|---|
| no further surprise | 99.4 | 96.0 | 4.55 | 120 | 20% |
| merchant_reader_issue@w7(high) + rival_new_fees@w4(base) + vendor_outage@w9(base) | 97.0 | 91.2 | 4.51 | 120 | 0% |
| post_migration_errors@w7(base) + viral_praise@w8(base) | 98.2 | 92.6 | 4.54 | 120 | 22% |
| rival_rate_poaching@w5(high) | 99.1 | 96.0 | 4.54 | 120 | 45% |
| viral_praise@w7(base) + rival_new_fees@w5(base) | 98.3 | 95.5 | 4.54 | 121 | 0% |
| phishing_wave@w8(low) + macro_rate_change@w7(low) | 98.6 | 96.9 | 4.52 | 121 | 40% |
| rival_outage@w5(low) + rival_rate_poaching@w4(base) | 98.2 | 96.4 | 4.54 | 120 | 45% |
| migration_overrun@w7(base) + positive_press@w7(base) + regulatory_or_media_probe@w9(base) | 96.2 | 91.6 | 4.51 | 120 | 0% |
| merchant_reader_issue@w7(base) + macro_rate_change@w6(low) | 98.6 | 96.2 | 4.55 | 120 | 62% |
| rivals_cut_rates@w8(high) | 99.6 | 95.5 | 4.57 | 126 | 18% |
| regulatory_or_media_probe@w9(base) | 98.0 | 95.8 | 4.54 | 140 | 22% |
| positive_press@w9(high) + paycheck_delay@w5(base) + rival_rate_poaching@w7(low) | 98.1 | 96.0 | 4.52 | 120 | 22% |
| government_shutdown_or_benefit_delay@w9(high) | 98.9 | 96.4 | 4.52 | 120 | 40% |

## Playbook: if this surprise is announced next, best response among the shortlisted plans
(a decision answering a surprise of week N can start in week N+1)

| if announced | best plan | utility | vs top plan |
|---|---|---|---|
| bad: A01_migration_overrun in week 6 | w4 | everyone | Early pay up to 2 days early [on]; Debit card cash back for 4 weeks [1%, up to $5]; Savings boost on new money only [+0.25 points]<br>w6 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Zero-interest advance up to $500 [on]; Goodwill credit to a defined group [$5 each] | -2.24 | +0.23 |
| bad: A02_post_migration_errors in week 7 | w6 | everyone | Early pay up to 2 days early [on]; Zero-interest advance up to $500 [on]<br>w7 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Debit card cash back for 4 weeks [1%, up to $5]; Savings boost on new money only [+0.25 points] | -0.73 | +0.55 |
| bad: A03_paycheck_delay in week 5 | w6 | everyone | Early pay up to 2 days early [on]; Zero-interest advance up to $500 [on]; Savings boost on new money only [+0.25 points]<br>w7 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Free replacement card on request and payment alerts [on]; Debit card cash back for 4 weeks [1%, up to $5] | 0.04 | +0.40 |
| bad: A04_phishing_wave in week 5 | w6 | everyone | Early pay up to 2 days early [on]; Zero-interest advance up to $500 [on]; Savings boost on new money only [+0.25 points]<br>w7 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Free replacement card on request and payment alerts [on]; Debit card cash back for 4 weeks [1%, up to $5] | -1.14 | +1.07 |
| bad: A05_card_fraud_or_breach in week 4 | w6 | everyone | Early pay up to 2 days early [on]; Zero-interest advance up to $500 [on]<br>w7 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Debit card cash back for 4 weeks [1%, up to $5]; Savings boost on new money only [+0.25 points] | -2.09 | +0.16 |
| bad: A06_rival_rate_poaching in week 4 | w5 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Debit card cash back for 4 weeks [1%, up to $5]; Zero-interest advance up to $500 [on]<br>w6 | everyone | Early pay up to 2 days early [on]; Goodwill credit to a defined group [$5 each]; Savings boost on new money only [+0.25 points] | 2.34 | +0.22 |
| bad: A07_rumor_solvency in week 5 | w6 | everyone | Early pay up to 2 days early [on]; Savings boost on new money only [+0.25 points]<br>w7 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Zero-interest advance up to $500 [on]; Debit card cash back for 4 weeks [1%, up to $5] | 0.73 | +0.00 |
| bad: A08_vendor_outage in week 3 | w6 | everyone | Early pay up to 2 days early [on]; Debit card cash back for 4 weeks [1%, up to $5]; Goodwill credit to a defined group [$5 each]<br>w7 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Zero-interest advance up to $500 [on]; Savings boost on new money only [+0.25 points] | 0.51 | +0.04 |
| bad: A09_merchant_reader_issue in week 4 | w5 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Debit card cash back for 4 weeks [1%, up to $5]; Zero-interest advance up to $500 [on]<br>w6 | everyone | Early pay up to 2 days early [on]; Goodwill credit to a defined group [$5 each]; Savings boost on new money only [+0.25 points] | 2.12 | +0.93 |
| bad: A10_regulatory_or_media_probe in week 3 | w4 | everyone | Early pay up to 2 days early [on]; Debit card cash back for 4 weeks [1%, up to $5]; Savings boost on new money only [+0.25 points]<br>w6 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Zero-interest advance up to $500 [on] | 0.30 | +0.97 |
| bad: A11_macro_rate_change in week 6 | w4 | everyone | Early pay up to 2 days early [on]; Debit card cash back for 4 weeks [1%, up to $5]; Savings boost on new money only [+0.25 points]<br>w6 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Zero-interest advance up to $500 [on]; Goodwill credit to a defined group [$5 each] | 2.07 | +0.98 |
| bad: A12_government_shutdown_or_benefit_delay in week 8 | w6 | everyone | Early pay up to 2 days early [on]; Goodwill credit to a defined group [$5 each]; Savings boost on new money only [+0.25 points]<br>w7 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Zero-interest advance up to $500 [on]; Debit card cash back for 4 weeks [1%, up to $5] | 0.74 | +0.67 |
| bad: A13_hq_weather_or_staffing in week 6 | w6 | everyone | Early pay up to 2 days early [on]; Goodwill credit to a defined group [$5 each]; Savings boost on new money only [+0.25 points]<br>w7 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Zero-interest advance up to $500 [on]; Debit card cash back for 4 weeks [1%, up to $5] | 2.45 | +0.78 |
| bad: A14_app_bug_or_login in week 6 | w4 | everyone | Early pay up to 2 days early [on]; Debit card cash back for 4 weeks [1%, up to $5]; Savings boost on new money only [+0.25 points]<br>w6 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Zero-interest advance up to $500 [on]; Goodwill credit to a defined group [$5 each] | 1.54 | +0.10 |
| good: G01_rival_outage in week 3 | w6 | everyone | Early pay up to 2 days early [on]; Savings boost on new money only [+0.25 points]<br>w7 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Zero-interest advance up to $500 [on]; Debit card cash back for 4 weeks [1%, up to $5] | 3.30 | +0.00 |
| good: G02_positive_press in week 3 | w4 | everyone | Early pay up to 2 days early [on]; Debit card cash back for 4 weeks [1%, up to $5]; Savings boost on new money only [+0.25 points]<br>w6 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Zero-interest advance up to $500 [on]; Goodwill credit to a defined group [$5 each] | 2.31 | +0.37 |
| good: G03_rivals_cut_rates in week 3 | w4 | everyone | Early pay up to 2 days early [on]; Debit card cash back for 4 weeks [1%, up to $5]; Savings boost on new money only [+0.25 points]<br>w6 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Zero-interest advance up to $500 [on]; Goodwill credit to a defined group [$5 each] | 1.29 | +1.00 |
| good: G04_viral_praise in week 3 | w4 | everyone | Early pay up to 2 days early [on]; Debit card cash back for 4 weeks [1%, up to $5]; Savings boost on new money only [+0.25 points]<br>w6 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Zero-interest advance up to $500 [on] | 2.78 | +0.38 |
| good: G05_rival_new_fees in week 3 | w4 | everyone | Early pay up to 2 days early [on]; Debit card cash back for 4 weeks [1%, up to $5]; Savings boost on new money only [+0.25 points]<br>w6 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Zero-interest advance up to $500 [on]; Goodwill credit to a defined group [$5 each] | 2.53 | +0.93 |

## Notes
- Utility: per goal weight x clip((value - target)/tol, -3, 1), weights and tolerances in params [optimize].
- The surrogate learned from LLM runs; it extrapolates poorly to surprise types and actions it rarely saw. Treat ranks, not decimals. Confirm the chosen plan with LLM runs before locking.
- Candidate messages are composed from factual snippets (messages.py); edit the wording before locking, keep the facts.
