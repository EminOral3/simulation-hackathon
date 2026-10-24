# Planner report: week 0 (earliest new decision: week 1)

Generated 13:32:26 in 230s. Surrogate `20261024-132836` (heldout log-loss vs base rate in meta). **Screening only: the hand-in runs are LLM runs.**

## Inputs
- Fixed decisions (week <= 0): none
- Budget left: $4.00M
- Surprises observed: none
- Migration overrun: unknown (averaged over on time / few hours / into Monday)
- Scenarios: 3 (no further surprise + random bad/good mixes), 1 reps each; searched 936 single-action and 6887 multi-action decisions, 10 final plans.

## No decision (business as usual from here)
goal_1 95.0 · goal_2 87.6 · goal_3 4.48 · goal_3b 120 · P(all goals) 0%

## Best plans (mean over scenarios; worst = lowest scenario utility)
| # | remaining decision(s) | cost | active % | deposits % | rating | CFPB/mo | P(all) | utility | worst |
|---|---|---|---|---|---|---|---|---|---|
| 1 | w6 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Debit card cash back for 4 weeks [2%, up to $10]; Zero-interest advance up to $500 [on] | $3.40M | 96.2 | 92.6 | 4.53 | 120 | 15% | -2.75 | -5.60 |
| 2 | w6 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Debit card cash back for 4 weeks [1%, up to $5]; Zero-interest advance up to $500 [on] | $2.40M | 95.8 | 92.5 | 4.53 | 120 | 15% | -2.94 | -5.76 |
| 3 | w6 | everyone | Savings rate boost for 4 weeks [+0.5 points]; Free instant transfers to other banks [2 weeks]; Debit card cash back for 4 weeks [1%, up to $5] | $2.90M | 95.5 | 92.7 | 4.52 | 120 | 15% | -3.12 | -5.91 |
| 4 | w6 | everyone | Savings rate boost for 4 weeks [+0.5 points]; Debit card cash back for 4 weeks [1%, up to $5]; Early pay up to 2 days early [on] | $3.30M | 95.6 | 92.6 | 4.53 | 120 | 0% | -3.15 | -5.78 |
| 5 | w6 | everyone | Savings rate boost for 4 weeks [+0.5 points]; Debit card cash back for 4 weeks [2%, up to $10] | $3.80M | 95.7 | 92.5 | 4.52 | 120 | 0% | -3.28 | -5.80 |
| 6 | w6 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Free instant transfers to other banks [4 weeks]; Debit card cash back for 4 weeks [1%, up to $5] | $2.20M | 95.0 | 92.9 | 4.52 | 120 | 15% | -3.35 | -5.80 |
| 7 | w6 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Debit card cash back for 4 weeks [1%, up to $5]; Free replacement card on request and payment alerts [on] | $2.30M | 95.4 | 92.7 | 4.52 | 120 | 0% | -3.40 | -5.73 |
| 8 | w6 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Instant dispute credit up to $100 per customer [on]; Debit card cash back for 4 weeks [2%, up to $10] | $3.40M | 94.9 | 92.7 | 4.52 | 120 | 15% | -3.39 | -5.91 |
| 9 | w6 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Free instant transfers to other banks [4 weeks]; Debit card cash back for 4 weeks [2%, up to $10] | $3.20M | 94.9 | 92.5 | 4.52 | 120 | 0% | -3.57 | -5.91 |
| 10 | w6 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Instant dispute credit up to $100 per customer [on]; Debit card cash back for 4 weeks [1%, up to $5] | $2.40M | 95.1 | 92.8 | 4.52 | 120 | 15% | -3.62 | -5.79 |

## When to act: best plan whose next decision starts in week w
| week | best plan | utility | P(all) |
|---|---|---|---|
| 6 | w6 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Debit card cash back for 4 weeks [2%, up to $10]; Zero-interest advance up to $500 [on] | -2.75 | 15% |

## Top plan per scenario
| scenario | active % | deposits % | rating | CFPB | all goals |
|---|---|---|---|---|---|
| no further surprise | 95.3 | 91.1 | 4.53 | 120 | 0% |
| regulatory_or_media_probe@w5(base) + rival_outage@w4(high) | 98.1 | 93.6 | 4.52 | 120 | 45% |
| merchant_reader_issue@w4(high) + rival_new_fees@w8(base) + hq_weather_or_staffing@w7(high) | 95.2 | 93.2 | 4.53 | 120 | 0% |

## Playbook: if this surprise is announced next, best response among the shortlisted plans
(a decision answering a surprise of week N can start in week N+1)

| if announced | best plan | utility | vs top plan |
|---|---|---|---|
| bad: A01_migration_overrun in week 6 | w6 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Debit card cash back for 4 weeks [2%, up to $10]; Zero-interest advance up to $500 [on] | -4.97 | +0.00 |
| bad: A02_post_migration_errors in week 7 | w6 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Debit card cash back for 4 weeks [2%, up to $10]; Zero-interest advance up to $500 [on] | -2.11 | +0.00 |
| bad: A03_paycheck_delay in week 5 | w6 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Debit card cash back for 4 weeks [1%, up to $5]; Zero-interest advance up to $500 [on] | -0.41 | +0.76 |
| bad: A04_phishing_wave in week 5 | w6 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Debit card cash back for 4 weeks [1%, up to $5]; Zero-interest advance up to $500 [on] | -1.79 | +0.00 |
| bad: A05_card_fraud_or_breach in week 4 | w6 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Free instant transfers to other banks [4 weeks]; Debit card cash back for 4 weeks [1%, up to $5] | -2.29 | +0.43 |
| bad: A06_rival_rate_poaching in week 4 | w6 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Debit card cash back for 4 weeks [2%, up to $10]; Zero-interest advance up to $500 [on] | 0.45 | +0.00 |
| bad: A07_rumor_solvency in week 5 | w6 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Free instant transfers to other banks [4 weeks]; Debit card cash back for 4 weeks [2%, up to $10] | -2.60 | +0.90 |
| bad: A08_vendor_outage in week 3 | w6 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Free instant transfers to other banks [4 weeks]; Debit card cash back for 4 weeks [1%, up to $5] | -1.83 | +0.35 |
| bad: A09_merchant_reader_issue in week 4 | w6 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Debit card cash back for 4 weeks [2%, up to $10]; Zero-interest advance up to $500 [on] | -1.54 | +0.00 |
| bad: A10_regulatory_or_media_probe in week 3 | w6 | everyone | Savings rate boost for 4 weeks [+0.5 points]; Debit card cash back for 4 weeks [2%, up to $10] | -3.80 | +0.29 |
| bad: A11_macro_rate_change in week 6 | w6 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Free instant transfers to other banks [4 weeks]; Debit card cash back for 4 weeks [1%, up to $5] | -2.49 | +1.40 |
| bad: A12_government_shutdown_or_benefit_delay in week 8 | w6 | everyone | Savings rate boost for 4 weeks [+0.5 points]; Debit card cash back for 4 weeks [1%, up to $5]; Early pay up to 2 days early [on] | -3.05 | +0.13 |
| bad: A13_hq_weather_or_staffing in week 6 | w6 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Debit card cash back for 4 weeks [1%, up to $5]; Free replacement card on request and payment alerts [on] | -3.03 | +0.30 |
| bad: A14_app_bug_or_login in week 6 | w6 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Debit card cash back for 4 weeks [2%, up to $10]; Zero-interest advance up to $500 [on] | 0.94 | +0.00 |
| good: G01_rival_outage in week 2 | w6 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Debit card cash back for 4 weeks [2%, up to $10]; Zero-interest advance up to $500 [on] | 0.27 | +0.00 |
| good: G02_positive_press in week 2 | w6 | everyone | Savings rate boost for 4 weeks [+0.5 points]; Free instant transfers to other banks [2 weeks]; Debit card cash back for 4 weeks [1%, up to $5] | -2.41 | +0.16 |
| good: G03_rivals_cut_rates in week 3 | w6 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Debit card cash back for 4 weeks [1%, up to $5]; Zero-interest advance up to $500 [on] | -2.56 | +0.55 |
| good: G04_viral_praise in week 2 | w6 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Debit card cash back for 4 weeks [1%, up to $5]; Zero-interest advance up to $500 [on] | -3.43 | +0.09 |
| good: G05_rival_new_fees in week 2 | w6 | everyone | Savings rate boost for 4 weeks [+0.25 points]; Debit card cash back for 4 weeks [2%, up to $10]; Zero-interest advance up to $500 [on] | -0.26 | +0.00 |

## Notes
- Utility: per goal weight x clip((value - target)/tol, -3, 1), weights and tolerances in params [optimize].
- The surrogate learned from LLM runs; it extrapolates poorly to surprise types and actions it rarely saw. Treat ranks, not decimals. Confirm the chosen plan with LLM runs before locking.
- Candidate messages are composed from factual snippets (messages.py); edit the wording before locking, keep the facts.
