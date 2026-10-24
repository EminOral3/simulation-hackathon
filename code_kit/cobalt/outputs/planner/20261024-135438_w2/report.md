# Planner report: week 2 (earliest new decision: week 3)

Generated 13:55:16 in 47s. Surrogate `20261024-133733` (heldout log-loss vs base rate in meta). **Screening only: the hand-in runs are LLM runs.**

## Inputs
- Fixed decisions (week <= 2): none
- Budget left: $4.00M
- Surprises observed: none
- Surrogate fidelity (run level, held-out LLM runs): goal_1 MAE 5.10 r 0.76; goal_2 MAE 6.42 r 0.71; goal_3 MAE 0.04 r 0.79; goal_3b MAE 18.13 r 0.08. CFPB is not informative when r < 0.3: judge it by the LLM check.
- Migration overrun: unknown (averaged over on time / few hours / into Monday)
- Scenarios: 4 (no further surprise + random bad/good mixes), 2 reps each; searched 748 single-action and 280 multi-action decisions, 541 final plans.

## No decision (business as usual from here)
goal_1 88.8 · goal_2 86.9 · goal_3 4.42 · goal_3b 120 · P(all goals) 0%

## Best plans (mean over scenarios; worst = lowest scenario utility)
| # | remaining decision(s) | cost | active % | deposits % | rating | CFPB/mo | P(all) | utility | worst |
|---|---|---|---|---|---|---|---|---|---|
| 1 | w6 | everyone | Early pay up to 2 days early [on]; Savings boost on new money only [+0.25 points]; Debit card cash back for 4 weeks [1%, up to $5]<br>w7 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Early pay up to 2 days early [on]; Zero-interest advance up to $500 [on] | $3.80M | 98.8 | 95.4 | 4.53 | 120 | 33% | 0.72 | -1.01 |
| 2 | w5 | everyone | Early pay up to 2 days early [on]; Debit card cash back for 4 weeks [1%, up to $5]; Savings boost on new money only [+0.25 points]<br>w7 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Early pay up to 2 days early [on]; Zero-interest advance up to $500 [on] | $3.80M | 98.5 | 95.7 | 4.50 | 120 | 42% | 0.70 | -1.29 |
| 3 | w6 | everyone | Early pay up to 2 days early [on]; Zero-interest advance up to $500 [on]; Savings boost on new money only [+0.25 points]<br>w7 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Early pay up to 2 days early [on]; Savings boost on new money only [+0.25 points] | $3.00M | 98.8 | 95.6 | 4.54 | 120 | 38% | 0.66 | -1.01 |
| 4 | w6 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Early pay up to 2 days early [on]; Savings boost on new money only [+0.25 points]<br>w7 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Early pay up to 2 days early [on]; Zero-interest advance up to $500 [on] | $3.40M | 98.8 | 95.6 | 4.55 | 120 | 32% | 0.65 | -1.86 |
| 5 | w6 | everyone | Early pay up to 2 days early [on]; Savings boost on new money only [+0.25 points]<br>w7 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Early pay up to 2 days early [on]; Zero-interest advance up to $500 [on] | $2.60M | 98.7 | 95.3 | 4.53 | 120 | 28% | 0.58 | -1.42 |
| 6 | w6 | everyone | Early pay up to 2 days early [on]; Zero-interest advance up to $500 [on]; Savings boost on new money only [+0.25 points]<br>w7 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Early pay up to 2 days early [on]; Debit card cash back for 4 weeks [1%, up to $5] | $3.80M | 99.1 | 95.2 | 4.54 | 120 | 33% | 0.52 | -0.76 |
| 7 | w6 | everyone | Early pay up to 2 days early [on]; Savings boost on new money only [+0.25 points]; Debit card cash back for 4 weeks [1%, up to $5]<br>w7 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Early pay up to 2 days early [on]; Savings boost on new money only [+0.25 points] | $3.80M | 98.3 | 95.8 | 4.52 | 126 | 42% | 0.48 | -1.25 |
| 8 | w4 | everyone | Early pay up to 2 days early [on]; Debit card cash back for 4 weeks [1%, up to $5]; Savings boost on new money only [+0.25 points]<br>w7 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Early pay up to 2 days early [on]; Zero-interest advance up to $500 [on] | $3.80M | 98.3 | 95.7 | 4.50 | 120 | 36% | 0.47 | -1.53 |
| 9 | w6 | everyone | Early pay up to 2 days early [on]; Zero-interest advance up to $500 [on]; Savings boost on new money only [+0.25 points]<br>w7 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Early pay up to 2 days early [on]; Zero-interest advance up to $500 [on] | $3.00M | 98.7 | 95.2 | 4.54 | 120 | 33% | 0.45 | -1.32 |
| 10 | w6 | everyone | Early pay up to 2 days early [on]; Zero-interest advance up to $500 [on]; Debit card cash back for 4 weeks [1%, up to $5]<br>w7 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Early pay up to 2 days early [on]; Savings boost on new money only [+0.25 points] | $3.80M | 99.2 | 95.0 | 4.54 | 120 | 33% | 0.44 | -0.71 |

## When to act: best plan whose next decision starts in week w
| week | best plan | utility | P(all) |
|---|---|---|---|
| 3 | w3 | everyone | Early pay up to 2 days early [on]; Zero-interest advance up to $500 [on]; Savings rate boost for 4 weeks [+0.25 points]<br>w7 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Early pay up to 2 days early [on]; Savings boost on new money only [+0.25 points] | 0.15 | 27% |
| 4 | w4 | everyone | Early pay up to 2 days early [on]; Debit card cash back for 4 weeks [1%, up to $5]; Savings boost on new money only [+0.25 points]<br>w7 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Early pay up to 2 days early [on]; Zero-interest advance up to $500 [on] | 0.47 | 36% |
| 5 | w5 | everyone | Early pay up to 2 days early [on]; Debit card cash back for 4 weeks [1%, up to $5]; Savings boost on new money only [+0.25 points]<br>w7 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Early pay up to 2 days early [on]; Zero-interest advance up to $500 [on] | 0.70 | 42% |
| 6 | w6 | everyone | Early pay up to 2 days early [on]; Savings boost on new money only [+0.25 points]; Debit card cash back for 4 weeks [1%, up to $5]<br>w7 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Early pay up to 2 days early [on]; Zero-interest advance up to $500 [on] | 0.72 | 33% |
| 7 | w7 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Early pay up to 2 days early [on]; Savings boost on new money only [+0.25 points]<br>w7 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Early pay up to 2 days early [on]; Zero-interest advance up to $500 [on] | -1.88 | 6% |

## Top plan per scenario
| scenario | active % | deposits % | rating | CFPB | all goals |
|---|---|---|---|---|---|
| no further surprise | 99.3 | 96.2 | 4.54 | 122 | 43% |
| merchant_reader_issue@w7(high) + rival_new_fees@w4(base) + vendor_outage@w9(base) | 97.9 | 93.3 | 4.50 | 120 | 22% |
| post_migration_errors@w7(base) + viral_praise@w8(base) | 98.9 | 94.8 | 4.54 | 120 | 22% |
| rival_rate_poaching@w5(high) | 99.3 | 97.4 | 4.54 | 120 | 45% |

## Playbook: if this surprise is announced next, best response among the shortlisted plans
(a decision answering a surprise of week N can start in week N+1)

| if announced | best plan | utility | vs top plan |
|---|---|---|---|
| bad: A01_migration_overrun in week 6 | w6 | everyone | Early pay up to 2 days early [on]; Savings boost on new money only [+0.25 points]; Debit card cash back for 4 weeks [1%, up to $5]<br>w7 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Early pay up to 2 days early [on]; Zero-interest advance up to $500 [on] | -0.17 | +0.00 |
| bad: A02_post_migration_errors in week 7 | w6 | everyone | Early pay up to 2 days early [on]; Zero-interest advance up to $500 [on]; Debit card cash back for 4 weeks [1%, up to $5]<br>w7 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Early pay up to 2 days early [on]; Savings boost on new money only [+0.25 points] | 0.09 | +0.07 |
| bad: A03_paycheck_delay in week 5 | w6 | everyone | Early pay up to 2 days early [on]; Savings boost on new money only [+0.25 points]<br>w7 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Early pay up to 2 days early [on]; Debit card cash back for 4 weeks [1%, up to $5] | 1.02 | +0.21 |
| bad: A04_phishing_wave in week 5 | w6 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Early pay up to 2 days early [on]; Savings boost on new money only [+0.25 points]<br>w7 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Early pay up to 2 days early [on]; Zero-interest advance up to $500 [on] | 0.63 | +1.06 |
| bad: A05_card_fraud_or_breach in week 4 | w5 | everyone | Early pay up to 2 days early [on]; Debit card cash back for 4 weeks [1%, up to $5]; Savings boost on new money only [+0.25 points]<br>w7 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Early pay up to 2 days early [on]; Zero-interest advance up to $500 [on] | -0.57 | +0.47 |
| bad: A06_rival_rate_poaching in week 4 | w6 | everyone | Early pay up to 2 days early [on]; Savings boost on new money only [+0.25 points]; Debit card cash back for 4 weeks [1%, up to $5]<br>w7 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Early pay up to 2 days early [on]; Savings boost on new money only [+0.25 points] | 3.23 | +0.04 |
| bad: A07_rumor_solvency in week 5 | w6 | everyone | Early pay up to 2 days early [on]; Zero-interest advance up to $500 [on]; Savings boost on new money only [+0.25 points]<br>w7 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Early pay up to 2 days early [on]; Debit card cash back for 4 weeks [1%, up to $5] | 1.90 | +0.81 |
| bad: A08_vendor_outage in week 3 | w6 | everyone | Early pay up to 2 days early [on]; Savings boost on new money only [+0.25 points]; Debit card cash back for 4 weeks [1%, up to $5]<br>w7 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Early pay up to 2 days early [on]; Savings boost on new money only [+0.25 points] | 1.82 | +0.47 |
| bad: A09_merchant_reader_issue in week 4 | w5 | everyone | Early pay up to 2 days early [on]; Debit card cash back for 4 weeks [1%, up to $5]; Savings boost on new money only [+0.25 points]<br>w6 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Zero-interest advance up to $500 [on]; Goodwill credit to a defined group [$5 each] | 3.13 | +0.86 |
| bad: A10_regulatory_or_media_probe in week 3 | w4 | everyone | Early pay up to 2 days early [on]; Debit card cash back for 4 weeks [1%, up to $5]; Savings boost on new money only [+0.25 points]<br>w6 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Zero-interest advance up to $500 [on]; Savings boost on new money only [+0.25 points] | 2.17 | +1.23 |
| bad: A11_macro_rate_change in week 6 | w4 | everyone | Early pay up to 2 days early [on]; Zero-interest advance up to $500 [on]; Savings boost on new money only [+0.25 points]<br>w7 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Early pay up to 2 days early [on]; Debit card cash back for 4 weeks [1%, up to $5] | 3.22 | +0.83 |
| bad: A12_government_shutdown_or_benefit_delay in week 8 | w6 | everyone | Early pay up to 2 days early [on]; Zero-interest advance up to $500 [on]; Savings boost on new money only [+0.25 points]<br>w7 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Early pay up to 2 days early [on]; Savings boost on new money only [+0.25 points] | 2.30 | +1.24 |
| bad: A13_hq_weather_or_staffing in week 6 | w4 | everyone | Early pay up to 2 days early [on]; Debit card cash back for 4 weeks [1%, up to $5]; Savings boost on new money only [+0.25 points]<br>w7 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Early pay up to 2 days early [on]; Zero-interest advance up to $500 [on] | 2.79 | +0.07 |
| bad: A14_app_bug_or_login in week 6 | w4 | everyone | Early pay up to 2 days early [on]; Debit card cash back for 4 weeks [1%, up to $5]; Savings boost on new money only [+0.25 points]<br>w7 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Early pay up to 2 days early [on]; Savings boost on new money only [+0.25 points] | 3.04 | +0.40 |
| good: G01_rival_outage in week 3 | w4 | everyone | Early pay up to 2 days early [on]; Debit card cash back for 4 weeks [1%, up to $5]; Savings boost on new money only [+0.25 points]<br>w6 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Zero-interest advance up to $500 [on]; Savings boost on new money only [+0.25 points] | 3.65 | +0.02 |
| good: G02_positive_press in week 3 | w4 | everyone | Early pay up to 2 days early [on]; Debit card cash back for 4 weeks [1%, up to $5]; Savings boost on new money only [+0.25 points]<br>w7 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Early pay up to 2 days early [on]; Zero-interest advance up to $500 [on] | 2.94 | +0.58 |
| good: G03_rivals_cut_rates in week 3 | w4 | everyone | Early pay up to 2 days early [on]; Debit card cash back for 4 weeks [1%, up to $5]; Savings boost on new money only [+0.25 points]<br>w6 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Zero-interest advance up to $500 [on]; Savings boost on new money only [+0.25 points] | 2.83 | +0.63 |
| good: G04_viral_praise in week 3 | w4 | everyone | Early pay up to 2 days early [on]; Debit card cash back for 4 weeks [1%, up to $5]; Savings boost on new money only [+0.25 points]<br>w6 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Zero-interest advance up to $500 [on]; Savings boost on new money only [+0.25 points] | 3.49 | +0.65 |
| good: G05_rival_new_fees in week 3 | w4 | everyone | Early pay up to 2 days early [on]; Debit card cash back for 4 weeks [1%, up to $5]; Savings boost on new money only [+0.25 points]<br>w7 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Early pay up to 2 days early [on]; Zero-interest advance up to $500 [on] | 3.34 | +0.74 |

## LLM check (real personas, lite, 1 seed, current announcements)
| plan | surrogate active/deposits | LLM active/deposits | LLM rating | LLM CFPB | run |
|---|---|---|---|---|---|
| no decision | 88.8 / 86.9 | 95.1 / 83.2 | 4.45 | 970 | `20261024-135516_nodecision_s1_mock-g3.5lite_planner-no decision` |
| plan_rank1 | 98.8 / 95.4 | 99.1 / 93.5 | 4.49 | 562 | `20261024-135516_plan_s1_mock-g3.5lite_planner-plan_rank1` |
| plan_rank2 | 98.5 / 95.7 | 94.8 / 92.9 | 4.45 | 934 | `20261024-135516_plan_s1_mock-g3.5lite_planner-plan_rank2` |
| plan_rank3 | 98.8 / 95.6 | 97.0 / 90.3 | 4.44 | 769 | `20261024-135516_plan_s1_mock-g3.5lite_planner-plan_rank3` |

## Notes
- Utility: per goal weight x clip((value - target)/tol, -3, 1), weights and tolerances in params [optimize].
- The surrogate learned from LLM runs; it extrapolates poorly to surprise types and actions it rarely saw. Treat ranks, not decimals. Confirm the chosen plan with LLM runs before locking.
- Candidate messages are composed from factual snippets (messages.py); edit the wording before locking, keep the facts.
