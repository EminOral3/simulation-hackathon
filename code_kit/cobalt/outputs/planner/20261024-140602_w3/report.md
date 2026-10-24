# Planner report: week 3 (earliest new decision: week 4)

Generated 14:06:56 in 189s. Surrogate `20261024-140550` (heldout log-loss vs base rate in meta). **Screening only: the hand-in runs are LLM runs.**

## Inputs
- Fixed decisions (week <= 3): none
- Budget left: $4.00M
- Surprises observed: none
- Surrogate fidelity (run level, held-out LLM runs): last check is older than this surrogate; rerun surrogate_check
- Migration overrun: unknown (averaged over on time / few hours / into Monday)
- Scenarios: 13 (no further surprise + random bad/good mixes), 2 reps each; searched 654 single-action and 247 multi-action decisions, 28 final plans.

## No decision (business as usual from here)
goal_1 92.6 · goal_2 90.3 · goal_3 4.46 · goal_3b 125 · P(all goals) 0%

## Best plans (mean over scenarios; worst = lowest scenario utility)
| # | remaining decision(s) | cost | active % | deposits % | rating | CFPB/mo | P(all) | utility | worst |
|---|---|---|---|---|---|---|---|---|---|
| 1 | w5 | everyone | Savings boost on new money only [+0.25 points]; Goodwill credit to a defined group [$5 each]<br>w6 | everyone | Offline card limit during migration $100 -> $250 [on]; Zero-interest advance up to $500 [on]; Early pay up to 2 days early [on] | $1.90M | 98.9 | 98.4 | 4.55 | 124 | 69% | 2.60 | -2.26 |
| 2 | w4 | everyone | Savings boost on new money only [+0.25 points]; Goodwill credit to a defined group [$5 each]<br>w6 | everyone | Offline card limit during migration $100 -> $250 [on]; Zero-interest advance up to $500 [on]; Early pay up to 2 days early [on] | $1.90M | 98.7 | 98.6 | 4.55 | 124 | 68% | 2.59 | -2.65 |
| 3 | w5 | everyone | Savings boost on new money only [+0.25 points]; Offline card limit during migration $100 -> $250 [on]<br>w6 | everyone | Goodwill credit to a defined group [$5 each]; Zero-interest advance up to $500 [on]; Early pay up to 2 days early [on] | $1.90M | 98.9 | 98.5 | 4.55 | 124 | 69% | 2.57 | -2.30 |
| 4 | w6 | everyone | Savings boost on new money only [+0.25 points]; Offline card limit during migration $100 -> $250 [on]<br>w6 | everyone | Goodwill credit to a defined group [$5 each]; Zero-interest advance up to $500 [on]; Early pay up to 2 days early [on] | $1.90M | 99.0 | 97.5 | 4.56 | 124 | 61% | 2.23 | -3.70 |
| 5 | w6 | everyone | Savings boost on new money only [+0.25 points]; Zero-interest advance up to $500 [on]<br>w6 | everyone | Goodwill credit to a defined group [$5 each]; Offline card limit during migration $100 -> $250 [on]; Early pay up to 2 days early [on] | $1.90M | 99.0 | 97.5 | 4.56 | 124 | 61% | 2.23 | -3.70 |
| 6 | w6 | everyone | Savings boost on new money only [+0.25 points]; Goodwill credit to a defined group [$5 each]<br>w6 | everyone | Offline card limit during migration $100 -> $250 [on]; Zero-interest advance up to $500 [on]; Early pay up to 2 days early [on] | $1.90M | 99.0 | 97.5 | 4.56 | 124 | 61% | 2.23 | -3.70 |
| 7 | w6 | everyone | Savings boost on new money only [+0.25 points]; Early pay up to 2 days early [on]<br>w6 | everyone | Goodwill credit to a defined group [$5 each]; Offline card limit during migration $100 -> $250 [on]; Zero-interest advance up to $500 [on] | $1.90M | 99.0 | 97.5 | 4.56 | 124 | 61% | 2.23 | -3.70 |
| 8 | w5 | everyone | Savings boost on new money only [+0.25 points]; Offline card limit during migration $100 -> $250 [on]; Savings rate boost for 4 weeks [+0.25 points]<br>w6 | everyone | Goodwill credit to a defined group [$5 each]; Zero-interest advance up to $500 [on]; Early pay up to 2 days early [on] | $2.70M | 98.9 | 97.5 | 4.56 | 124 | 61% | 2.22 | -2.54 |
| 9 | w6 | everyone | Goodwill credit to a defined group [$5 each]; Offline card limit during migration $100 -> $250 [on]; Early pay up to 2 days early [on]<br>w7 | everyone | Savings boost on new money only [+0.25 points]; Zero-interest advance up to $500 [on] | $1.90M | 99.1 | 97.2 | 4.54 | 124 | 55% | 2.11 | -3.00 |
| 10 | w6 | everyone | Goodwill credit to a defined group [$5 each]; Offline card limit during migration $100 -> $250 [on]; Zero-interest advance up to $500 [on]<br>w7 | everyone | Savings boost on new money only [+0.25 points]; Early pay up to 2 days early [on] | $1.90M | 99.0 | 97.0 | 4.54 | 124 | 55% | 2.02 | -2.31 |

## When to act: best plan whose next decision starts in week w
| week | best plan | utility | P(all) |
|---|---|---|---|
| 4 | w4 | everyone | Savings boost on new money only [+0.25 points]; Goodwill credit to a defined group [$5 each]<br>w6 | everyone | Offline card limit during migration $100 -> $250 [on]; Zero-interest advance up to $500 [on]; Early pay up to 2 days early [on] | 2.59 | 68% |
| 5 | w5 | everyone | Savings boost on new money only [+0.25 points]; Goodwill credit to a defined group [$5 each]<br>w6 | everyone | Offline card limit during migration $100 -> $250 [on]; Zero-interest advance up to $500 [on]; Early pay up to 2 days early [on] | 2.60 | 69% |
| 6 | w6 | everyone | Savings boost on new money only [+0.25 points]; Offline card limit during migration $100 -> $250 [on]<br>w6 | everyone | Goodwill credit to a defined group [$5 each]; Zero-interest advance up to $500 [on]; Early pay up to 2 days early [on] | 2.23 | 61% |

## Top plan per scenario
| scenario | active % | deposits % | rating | CFPB | all goals |
|---|---|---|---|---|---|
| no further surprise | 98.9 | 98.4 | 4.58 | 122 | 50% |
| rival_rate_poaching@w5(base) | 99.9 | 97.9 | 4.58 | 120 | 77% |
| viral_praise@w9(low) + merchant_reader_issue@w6(high) | 99.6 | 98.4 | 4.57 | 120 | 90% |
| positive_press@w4(low) + regulatory_or_media_probe@w9(high) | 98.4 | 97.3 | 4.55 | 124 | 55% |
| government_shutdown_or_benefit_delay@w10(base) + rumor_solvency@w7(high) + phishing_wave@w5(base) | 95.3 | 94.7 | 4.49 | 121 | 22% |
| merchant_reader_issue@w8(high) + paycheck_delay@w6(base) | 98.6 | 99.4 | 4.53 | 120 | 100% |
| positive_press@w10(base) | 99.1 | 99.0 | 4.58 | 120 | 68% |
| rival_new_fees@w9(base) + macro_rate_change@w7(high) | 100.0 | 100.1 | 4.57 | 120 | 100% |
| merchant_reader_issue@w6(high) + positive_press@w9(base) + rival_rate_poaching@w9(low) | 99.8 | 99.8 | 4.58 | 120 | 100% |
| viral_praise@w5(base) + rival_new_fees@w9(base) | 99.5 | 97.7 | 4.58 | 120 | 40% |
| paycheck_delay@w6(base) + macro_rate_change@w6(base) | 98.4 | 99.1 | 4.52 | 120 | 68% |
| paycheck_delay@w9(high) + migration_overrun@w6(base) + paycheck_delay@w5(low) | 98.3 | 98.0 | 4.49 | 126 | 45% |
| rivals_cut_rates@w7(base) | 99.6 | 99.3 | 4.58 | 161 | 77% |

## Playbook: if this surprise is announced next, best response among the shortlisted plans
(a decision answering a surprise of week N can start in week N+1)

| if announced | best plan | utility | vs top plan |
|---|---|---|---|
| bad: A01_migration_overrun in week 6 | w4 | everyone | Savings boost on new money only [+0.25 points]; Goodwill credit to a defined group [$5 each]<br>w6 | everyone | Offline card limit during migration $100 -> $250 [on]; Zero-interest advance up to $500 [on]; Early pay up to 2 days early [on] | 3.30 | +0.13 |
| bad: A02_post_migration_errors in week 7 | w4 | everyone | Savings boost on new money only [+0.25 points]; Goodwill credit to a defined group [$5 each]<br>w6 | everyone | Offline card limit during migration $100 -> $250 [on]; Zero-interest advance up to $500 [on]; Early pay up to 2 days early [on] | 2.42 | +0.48 |
| bad: A03_paycheck_delay in week 5 | w4 | everyone | Savings boost on new money only [+0.25 points]; Goodwill credit to a defined group [$5 each]<br>w6 | everyone | Offline card limit during migration $100 -> $250 [on]; Zero-interest advance up to $500 [on]; Early pay up to 2 days early [on] | 2.95 | +0.01 |
| bad: A04_phishing_wave in week 5 | w4 | everyone | Savings boost on new money only [+0.25 points]; Goodwill credit to a defined group [$5 each]<br>w6 | everyone | Offline card limit during migration $100 -> $250 [on]; Zero-interest advance up to $500 [on]; Early pay up to 2 days early [on] | 3.11 | +0.35 |
| bad: A05_card_fraud_or_breach in week 4 | w4 | everyone | Savings boost on new money only [+0.25 points]; Goodwill credit to a defined group [$5 each]<br>w6 | everyone | Offline card limit during migration $100 -> $250 [on]; Zero-interest advance up to $500 [on]; Early pay up to 2 days early [on] | 2.90 | +0.40 |
| bad: A06_rival_rate_poaching in week 4 | w5 | everyone | Savings boost on new money only [+0.25 points]; Goodwill credit to a defined group [$5 each]<br>w6 | everyone | Offline card limit during migration $100 -> $250 [on]; Zero-interest advance up to $500 [on]; Early pay up to 2 days early [on] | 4.01 | +0.00 |
| bad: A07_rumor_solvency in week 5 | w4 | everyone | Savings boost on new money only [+0.25 points]; Goodwill credit to a defined group [$5 each]<br>w6 | everyone | Offline card limit during migration $100 -> $250 [on]; Zero-interest advance up to $500 [on]; Early pay up to 2 days early [on] | 3.28 | +0.43 |
| bad: A08_vendor_outage in week 4 | w5 | everyone | Savings boost on new money only [+0.25 points]; Offline card limit during migration $100 -> $250 [on]<br>w6 | everyone | Goodwill credit to a defined group [$5 each]; Zero-interest advance up to $500 [on]; Early pay up to 2 days early [on] | 3.48 | +0.14 |
| bad: A09_merchant_reader_issue in week 4 | w4 | everyone | Savings boost on new money only [+0.25 points]; Goodwill credit to a defined group [$5 each]<br>w6 | everyone | Offline card limit during migration $100 -> $250 [on]; Zero-interest advance up to $500 [on]; Early pay up to 2 days early [on] | 3.64 | +0.04 |
| bad: A10_regulatory_or_media_probe in week 5 | w4 | everyone | Savings boost on new money only [+0.25 points]; Goodwill credit to a defined group [$5 each]<br>w6 | everyone | Offline card limit during migration $100 -> $250 [on]; Zero-interest advance up to $500 [on]; Early pay up to 2 days early [on] | 2.90 | +0.48 |
| bad: A11_macro_rate_change in week 6 | w5 | everyone | Savings boost on new money only [+0.25 points]; Goodwill credit to a defined group [$5 each]<br>w6 | everyone | Offline card limit during migration $100 -> $250 [on]; Zero-interest advance up to $500 [on]; Early pay up to 2 days early [on] | 3.82 | +0.00 |
| bad: A12_government_shutdown_or_benefit_delay in week 8 | w6 | everyone | Goodwill credit to a defined group [$5 each]; Offline card limit during migration $100 -> $250 [on]; Early pay up to 2 days early [on]<br>w7 | everyone | Savings boost on new money only [+0.25 points]; Zero-interest advance up to $500 [on] | 3.66 | +0.14 |
| bad: A13_hq_weather_or_staffing in week 6 | w5 | everyone | Savings boost on new money only [+0.25 points]; Offline card limit during migration $100 -> $250 [on]<br>w6 | everyone | Goodwill credit to a defined group [$5 each]; Zero-interest advance up to $500 [on]; Early pay up to 2 days early [on] | 3.79 | +0.14 |
| bad: A14_app_bug_or_login in week 6 | w4 | everyone | Savings boost on new money only [+0.25 points]; Goodwill credit to a defined group [$5 each]<br>w6 | everyone | Offline card limit during migration $100 -> $250 [on]; Zero-interest advance up to $500 [on]; Early pay up to 2 days early [on] | 3.74 | +0.17 |
| good: G01_rival_outage in week 4 | w5 | everyone | Savings boost on new money only [+0.25 points]; Offline card limit during migration $100 -> $250 [on]<br>w6 | everyone | Goodwill credit to a defined group [$5 each]; Zero-interest advance up to $500 [on]; Early pay up to 2 days early [on] | 3.83 | +0.25 |
| good: G02_positive_press in week 4 | w5 | everyone | Savings boost on new money only [+0.25 points]; Offline card limit during migration $100 -> $250 [on]<br>w6 | everyone | Goodwill credit to a defined group [$5 each]; Zero-interest advance up to $500 [on]; Early pay up to 2 days early [on] | 3.85 | +0.01 |
| good: G03_rivals_cut_rates in week 4 | w5 | everyone | Savings boost on new money only [+0.25 points]; Offline card limit during migration $100 -> $250 [on]<br>w6 | everyone | Goodwill credit to a defined group [$5 each]; Zero-interest advance up to $500 [on]; Early pay up to 2 days early [on] | 3.09 | +0.09 |
| good: G04_viral_praise in week 4 | w4 | everyone | Savings boost on new money only [+0.25 points]; Goodwill credit to a defined group [$5 each]<br>w6 | everyone | Offline card limit during migration $100 -> $250 [on]; Zero-interest advance up to $500 [on]; Early pay up to 2 days early [on] | 3.74 | +0.09 |
| good: G05_rival_new_fees in week 4 | w5 | everyone | Savings boost on new money only [+0.25 points]; Offline card limit during migration $100 -> $250 [on]<br>w6 | everyone | Goodwill credit to a defined group [$5 each]; Zero-interest advance up to $500 [on]; Early pay up to 2 days early [on] | 3.84 | +0.03 |

## LLM check (real personas, lite, 1 seed, current announcements)
| plan | surrogate active/deposits | LLM active/deposits | LLM rating | LLM CFPB | run |
|---|---|---|---|---|---|
| no-decision | 92.6 / 90.3 | 98.9 / 97.2 | 4.55 | 120 | `20261024-140656_nodecision_s1_g3.5lite_planner-no-decision` |
| plan_rank1 | 98.9 / 98.4 | 99.7 / 98.0 | 4.59 | 120 | `20261024-140656_plan_s1_g3.5lite_planner-plan_rank1` |
| plan_rank2 | 98.7 / 98.6 | 100.0 / 100.2 | 4.58 | 120 | `20261024-140656_plan_s1_g3.5lite_planner-plan_rank2` |
| plan_rank3 | 98.9 / 98.5 | 100.0 / 100.6 | 4.60 | 120 | `20261024-140656_plan_s1_g3.5lite_planner-plan_rank3` |

## Notes
- Utility: per goal weight x clip((value - target)/tol, -3, 1), weights and tolerances in params [optimize].
- The surrogate learned from LLM runs; it extrapolates poorly to surprise types and actions it rarely saw. Treat ranks, not decimals. Confirm the chosen plan with LLM runs before locking.
- Candidate messages are composed from factual snippets (messages.py); edit the wording before locking, keep the facts.
