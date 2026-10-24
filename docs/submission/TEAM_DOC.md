# TEAM_DOC: how we built the Cobalt simulation (team-04)

Code: `code/code_kit/cobalt/` (entry points `run.py`, `experiments.py`, `planner.py`, `package.py`; all parameters in `params/default.toml`). Hand-in runs: `bash code_kit/cobalt/final_runs.sh live` (gemini-3.7-flash). Experiments: gemini-3.5-flash-lite.

## Personas (75, all five dossier groups)
- **Distribution first, story second.** Each group has 4 behavioural axes chosen for this case (e.g. savers: rate seeking, FDIC exposure, rumour style, voice; paycheck: fragility, main/second bank, rumour style, voice). 16-person groups are a full 2^4 factorial, 8-person groups a 2^(4-1) half fraction, so every driver is covered; post-stratification weights (customers each persona stands for) restore representativeness. Cells heavier than 75k customers are split into clones with different stories.
- Group sizes and deposits reconcile to the dossier (2.1M customers, 1.0M active, $6.0B deposits, half with 5% of customers). Anchors: Fed SHED (37% cannot cover $400 in cash; 21% fraud/scam victims) [partly verified, secondary]; everything else is labelled VARSAYIM in `population_priors.json`.
- Code samples every field consistently with the axes; the LLM only writes a 4-6 sentence backstory from those fields, then a second call checks it against the fields; sensitive-word and near-duplicate scans trigger rewrites (75/75 passed). Stories may not predict crisis reactions.
- Used: balance band, paycheck into Cobalt and payday (Dec 11 vs Dec 12 freeze), main/second bank, number of banks, moves money for rate, knows FDIC limit, paycheck to paycheck, fraud/phishing history, reaction to bank texts, P2P use, app use, support channel, news sources, opinion leader, rumour style, voice, patience, forgiveness, card-reader ticket size. Left out: catalog section I (zodiac, colour, shoe size...) except one human detail; card design, dark mode. No sensitive traits.
- Compared against a hand-written 40-person panel (one run): same behaviour, but one persona = 6% of active customers (coarser than the 2-point goal tolerance), all 40 stories end with the same scripted crisis sentence, and rate seekers are 3% of weight. Kept 75.

## The world
- Each week, two LLM calls per persona. Round A (react and talk): private messages (up to 2) and a question to people in their tie network (3-8 ties, homophily, leaders better connected), public posts on the channels they use. Round B (decide): sees the same week's messages, posts and questions; returns actions, review, support contact, CFPB, money moved/added, a memory note it writes for itself, and status. Weekly status and the call id come from round B.
- Code (deterministic, seeded, common random numbers between plan and no-decision runs): calendar, company messages word for word and only to the target, business as usual (migration email Dec 5, holding statements), the migration weekend (P2P failures, declined payments over the offline limit, Friday paycheck trapped unless early pay), rival rate ads in weeks 5-7, support queue (Erlang C: contacts this week give next week's wait), dispute credits.
- Metrics: ratios to Nov 2, weighted by customers per persona; say-do conversion 0.69 (J.D. Power: 13% say they may switch, 9% do) [secondary source]; versioned metrics v2 (28-day activity proxy, CFPB reported as not measurable when events are rare).

## How we read each crisis
- **Week 3, unrecognized small charges + "Cobalt got hacked" post:** card fraud plus rumour; fast; earliest answer week 4. Personally hit: the true share from the week-4 update (about 9,000 of 2.1M), small amounts.
- **Week 4 update:** processor fault plus fraud tests on cards stolen elsewhere, no breach: the scare shrinks; open risks move to the upgrade and deposits.
- **Week 6 migration (known), outcome announced in week 7:** about four hours late; used as the fixed outcome in every run including plan_nosurprises.
- **Week 7 shutdown, week 8 update:** hits federal-employee paycheck customers (Dec 30 paycheck); Postal Service continues, so postal workers are not hit.

## Experiments (about 230 LLM runs, mostly lite, 1-2 seeds)
- Week 3: 16 decision sets (act in week 4 vs wait, use the second decision now or later). Week 4: 17 sets, then a 2^4 factorial (week 6 vs 8, boost size, support level, message) with Lenth effects: week 6 better (active +7.8), boost helps only in week 6. Then 32 variants around the winner: the "security" message was the only consistent gain; SMS and CEO video did not help.
- A surrogate (logistic model trained on 24,000 persona-weeks from 64 LLM runs) plus a vectorized simulator screened about 1,000 decisions per scenario in seconds for a weekly planner; held-out run-level fit r = 0.49-0.72. Screening only; every decision was confirmed with LLM runs.
- Network on/off and lite vs 3.7 comparisons (below).

## What we learned and problems we hit
- **Over-reaction.** Early runs lost half the customers. Fixes, each tied to evidence, not to the goals: realistic status definitions (closing needs paycheck and autopays moved), say-do conversion, and a bug: a crisis template gave every persona who saw the news an $87 unknown charge (true incidence 0.4%); 69% contacted support in one week. After the fixes a no-decision, no-surprise run lost 0.7% active and 1.2% deposits, inside our sanity bounds.
- **Model matters.** With lite, plan and no-decision were both near target and indistinguishable; with 3.7 (hand-in) personas leave more readily (10-week losses 9-21%), and the plan keeps 4-5 points more deposits. Our early decisions were chosen on runs that still had the bug; their measured advantage then was partly an artifact.
- Interaction: peers drive most late exits in the hand-in runs; switching the network off in lite runs did not move the goals measurably (2 seeds).
- Cost: lean prompts, salient-only round A and one-seed screening cut API use by about a third per run; 3.7 latency tails fixed with a 10 s timeout (five runs in 8-9 minutes).

## With more time
More seeds per arm and a lite/3.7 calibration on the same anchors; a calibrated CFPB proxy; a small real-customer panel to correct the synthetic one (prediction-powered inference); human review of personas.
