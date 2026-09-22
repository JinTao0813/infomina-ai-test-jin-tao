# Location entropy interview questions and answers

Use this as a recall guide, not a script to memorize. Read a question, answer it aloud in 30 to 60 seconds, then compare your answer with the notes.

A strong interview answer usually has four parts:

1. State what I did.
2. Explain why.
3. Give one result or piece of evidence.
4. State the limitation.

## Core questions

### 1. What is location entropy in plain English?

Location entropy measures how predictable a user's recorded locations are. Low entropy means their check-ins are concentrated at a small number of venues. High entropy means their check-ins are distributed more evenly across their observed venues. It measures a pattern in recorded check-ins, not personality, distance travelled, or willingness to explore.

### 2. How is entropy calculated from check-in counts?

For each user, I count their check-ins at each venue. I divide each venue count by the user's total check-ins to obtain the probability of that venue. I then calculate:

\[
H_u=-\sum_i p_u(i)\log_2 p_u(i)
\]

The result is the probability-weighted average surprise of the user's recorded venues.

### 3. What does "surprise" mean in this formula?

The surprise of an event is \(-\log_2(p)\). A common venue has high probability and low surprise. A rare venue has low probability and high surprise. The number of check-ins is not itself the surprise. Counts are used to estimate probabilities, and the probabilities determine surprise.

### 4. What is the difference between raw and normalized entropy?

Raw entropy is measured in bits and can grow when a user has more unique venues. Normalized entropy divides raw entropy by the maximum possible entropy for that user's observed venue count:

\[
H_{norm}=\frac{H}{\log_2(K)}
\]

Here, \(K\) is the number of unique observed venues. The normalized value ranges from 0 to 1 and describes evenness within the user's observed venue set.

### 5. What does high or low entropy mean for a user?

Low entropy means a few venues account for most recorded visits. High entropy means visits are distributed more evenly. It does not mean a high-entropy user travels farther, visits more venues, or prefers novel recommendations. Those require separate measurements or experiments.

### 6. Why did you choose this dataset?

The assignment allowed any public spatio-temporal dataset. I could not access the suggested EPFL dataset, so I selected the public Foursquare TSMC 2014 NYC and Tokyo check-in dataset. It contains anonymized user IDs, venue IDs, categories, coordinates, and timestamps, which are sufficient for calculating per-user venue entropy and comparing time contexts.

### 7. How did you clean and validate the data?

I loaded each headerless Latin-1 TSV with an explicit eight-column schema and explicit data types. The loader rejects malformed field counts, blank required fields, invalid coordinates, and invalid timestamps. I removed only exact duplicate source rows. I also checked timezone offsets and venue metadata conflicts. The two source files contained no malformed, blank, or invalid-coordinate rows.

### 8. What were your main findings?

Median normalized venue entropy was similar in NYC at 0.853 and Tokyo at 0.860. Differences between users were larger than the 0.007 city-median gap. Among users with at least 20 check-ins in each time context, most had higher weekend entropy. Venue entropy and category entropy were related but not interchangeable.

### 9. Why did you compare weekdays and weekends?

The timestamps allowed me to test whether recorded location patterns changed with temporal context. I calculated entropy separately for each user's local weekday and weekend events. This was a paired comparison, so each user was compared with themselves rather than with a different group of users.

### 10. What product idea did the findings motivate?

They motivated Context-Aware Discovery. The hypothesis is that venue recommendations might improve when explicit user preference is combined cautiously with observed profile diversity, reliable temporal context, candidate novelty, and category familiarity. The analysis motivates this idea but does not validate it.

### 11. What can you claim, and what can you not claim?

I can describe patterns in this historical sample: similar city medians, higher weekend entropy for most eligible users, and a difference between venue and category diversity. I cannot claim that weekends cause exploration, that city residents behave this way in general, that high-entropy users want novelty, or that the prototype improves recommendations.

### 12. How would you make this solution production-ready?

I would define a versioned event schema, store validated events in partitioned Parquet, use incremental or distributed aggregation, and monitor schema drift, missing values, duplicates, timezone anomalies, and metric distributions. I would also define data retention and consent rules, estimate metric confidence, test thresholds, and validate any product use with a randomized experiment.

## Entropy questions

### 13. Calculate entropy for `A, A, A, B`.

The probabilities are 0.75 for A and 0.25 for B:

\[
H=-(0.75\log_2 0.75+0.25\log_2 0.25)\approx0.811
\]

A is common, so it contributes little surprise per event. B is rare, so it has more surprise. Their probability-weighted average is about 0.811 bits.

### 14. What happens when a user visits only one venue?

That venue has probability 1. Since \(\log_2(1)=0\), raw entropy is 0. Normalization would otherwise divide by \(\log_2(1)=0\), so the function explicitly defines normalized entropy as 0 for one observed location.

### 15. Why use base-2 logarithms?

Base 2 expresses entropy in bits and matches the conventional information-theory interpretation. Another log base would preserve ordering but change the unit. Because normalized entropy divides by a logarithm using the same base, its value would not change.

### 16. Why does a rare venue have more surprise than a common venue?

Surprise is inversely related to probability. An event with probability 0.5 has one bit of surprise, while an event with probability 0.125 has three bits. Seeing a rare event gives more information because it was harder to predict.

### 17. Can users with different numbers of venues have the same normalized entropy?

Yes. A user split evenly across two venues and another split evenly across 100 venues both have normalized entropy 1. They have equal evenness relative to their own observed sets, but not equal venue variety. This is why I report unique venue count and raw entropy with normalized entropy.

### 18. Why is normalized entropy not enough on its own?

It hides the size of the observed venue set and remains affected by observation count and check-in behavior. A normalized value of 1 could come from two venues or 100 venues. It should be interpreted with total check-ins, unique venues, raw entropy, and data confidence.

### 19. How does observation count affect entropy?

Short histories can produce unstable estimates and may miss less frequent venues. Longer histories have more opportunity to reveal a user's venue distribution. Normalization improves one form of comparability but does not remove sampling bias. In this dataset, normalized entropy also showed a relationship with activity count.

### 20. Does high entropy mean someone is adventurous?

No. Entropy only describes the distribution of recorded check-ins. High entropy could result from work, travel, data collection habits, or many other causes. Calling it adventurous would turn a descriptive metric into an unsupported personality label.

### 21. Why not use unique venue count instead of entropy?

Unique venue count measures variety but ignores concentration. Two users can visit ten venues while one visits them evenly and the other makes 90 percent of visits at one venue. Entropy captures that distribution. I keep both because they answer different questions.

### 22. Could you calculate entropy with categories or geographic cells?

Yes. The function accepts a configurable location column. In the analysis, I use venue IDs for location entropy and category IDs for activity-category entropy. Geographic cells could measure spatial spread at a chosen resolution, but the grid size would become an important modeling decision.

### 23. How would distance-aware entropy differ?

Standard entropy treats every distinct venue as a separate symbol and ignores physical distance. A distance-aware metric could cluster nearby venues, use grid cells, or combine entropy with radius of gyration or travel distance. That would answer a different question about spatial movement rather than only visit predictability.

## Data preparation questions

### 24. How did you determine the encoding and file structure?

The dataset documentation describes two TSV files with eight columns and no header. Manual inspection showed that Latin-1 decoding was needed for category labels. I encoded that knowledge explicitly in the loader instead of relying on automatic inference.

### 25. Why remove exact duplicates?

Exact duplicate events would receive extra probability mass and bias the distribution. I only removed rows identical across all source columns. Deduplicating by user and venue would be wrong because repeat visits are genuine behavior needed by the entropy calculation.

### 26. Did you remove malformed rows or reject them?

I reject malformed or invalid input rather than silently dropping it. Silent removal could hide upstream data problems and make row counts difficult to audit. The actual source files passed the malformed, blank-field, coordinate, and timestamp checks.

### 27. Which data-quality problems did you find?

I found 250 exact duplicates in NYC and 577 in Tokyo. I also found supplied timezone offsets inconsistent with the city on 456 NYC rows and 27 Tokyo rows. Some venues had conflicting category or coordinate metadata. No malformed, blank, or invalid-coordinate rows passed validation.

### 28. Why identify users with both city and user ID?

The numerical user ID space restarts or overlaps between files. There are 3,376 distinct city-user pairs but only 2,293 distinct bare user IDs. Using only `user_id` would incorrectly merge NYC and Tokyo users, so the analysis groups by `(city, user_id)`.

### 29. Why calculate local time from the city timezone?

Weekday and weekend labels depend on local time. Named IANA timezones such as `America/New_York` and `Asia/Tokyo` handle the city's actual local-time rules. The supplied offsets contained inconsistent values, so I retained them for quality reporting but did not treat them as authoritative.

### 30. Why not trust the supplied timezone offset?

Hundreds of rows had offsets inconsistent with their city. A fixed offset can also mishandle daylight-saving transitions. Converting the parsed UTC timestamp with a named city timezone gives a consistent local-time rule.

### 31. Why retain `Home (private)` check-ins in the analysis?

They are part of the observed routine and removing one category could change the entropy distribution differently across cities. I retained them for the aggregate historical analysis, reported their prevalence, and treated them as a privacy and measurement limitation. I excluded private-home, workplace, and residential categories from prototype candidates.

### 32. How did you handle conflicting venue categories or coordinates?

I reported the conflicts instead of inventing corrections without a reliable reference table. Venue entropy uses venue IDs, so it does not require repaired coordinates. Category entropy uses each event's recorded category ID. In production, I would version and validate venue metadata against an authoritative source.

### 33. Why use category IDs instead of category names?

Names are display labels and may merge, change, or contain formatting differences. Recorded category IDs preserve the source event's categorical identity. The dataset also showed that IDs and labels were not one-to-one, so I avoided unsupported canonicalization.

### 34. What happens if a required value is null?

The loader fails with a clear error that names the invalid fields and counts. The entropy function also rejects null group keys or null location keys. This prevents pandas grouping behavior from silently excluding observations.

### 35. How would you process a file too large for memory?

I would validate and aggregate data in partitions. Each partition can produce counts by user and venue, which can then be summed globally before calculating probabilities and entropy. Parquet partitioning with Polars, DuckDB, Spark, or a warehouse would be more appropriate than loading the full raw TSV into pandas.

## Implementation questions

### 36. Walk through `calculate_location_entropy`.

The function validates group and location columns, handles empty input, and rejects null keys. It groups events by the requested group columns and location to get counts. It divides each location count by the group total, calculates \(-p\log_2p\), and sums those components per group. It then returns observation count, unique-location count, raw entropy, and normalized entropy.

### 37. Why use vectorized pandas operations instead of Python loops?

Groupby and array operations move most work into optimized library code, reduce Python overhead, and make the calculation shorter and easier to test. They also provide a clearer path to equivalent SQL or distributed aggregations. A Python loop over every user and event would scale poorly.

### 38. Why accept configurable group and location columns?

It keeps the metric reusable. I can group by `user_id`, by `(city, user_id)`, or by `(city, user_id, context)`, and I can treat venue ID or category ID as the location variable. The interface remains small and does not contain dataset-specific file logic.

### 39. What does the function return?

For each group, it returns the group key columns, `observation_count`, `unique_location_count`, raw `entropy` in bits, and `normalized_entropy` from 0 to 1.

### 40. How does it handle empty input?

It returns an empty DataFrame with the documented output columns. Returning a stable schema makes downstream pipelines easier to compose than returning `None` or a differently shaped object.

### 41. How does it handle a group with one location?

Raw entropy is 0. The function defines normalized entropy as 0 instead of dividing by zero. A test verifies this behavior.

### 42. How do you prevent users from different cities being combined?

Every main calculation includes both `city` and `user_id` in its group columns. Tests also verify that the same bare ID in NYC and Tokyo remains two independent users.

### 43. What is the time complexity?

The main cost is grouping \(n\) rows into \(m\) unique group-location pairs. Hash-based grouping is approximately linear in \(n\) on average, although pandas implementation details and sorting can change the practical cost. Memory is approximately proportional to the number of unique group-location pairs.

### 44. How would you implement it in SQL, Spark, or Polars?

First aggregate `COUNT(*)` by user and location. Then use a window sum to calculate each user's total, derive probability, and sum `-p * log2(p)` by user. Unique location count comes from the size of the first aggregate. Spark and Polars can express the same two-stage grouped calculation.

### 45. How would you calculate entropy incrementally?

I would store per-user per-location counts and each user's total count. New events update those sufficient statistics. Entropy can then be recomputed from the updated counts, or maintained using an equivalent count-based identity. I would also define event-time windows and correction rules because unbounded lifetime entropy may become stale.

### 46. What tests did you write?

Tests cover one-location entropy, uniform distributions, the hand-calculated 3-to-1 case, composite groups, missing columns, null keys, and empty input. Loader tests cover encoding, timezone conversion, duplicates, malformed fields, coordinates, timestamps, unknown cities, and overlapping user IDs. API tests cover ranking calculations, fallback behavior, validation, deterministic ties, and safe output fields.

### 47. Which test gives you the most confidence in the formula?

The hand-calculated unequal distribution test is the strongest direct check. For counts `[3, 1]`, it compares the implementation with the explicit mathematical result. Uniform and one-location tests then verify the important boundaries.

### 48. What production monitoring would you add?

I would monitor row volume, schema changes, null rates, malformed rows, duplicate rates, timezone anomalies, unseen categories, venue metadata conflicts, user activity distributions, and entropy distributions. Alerts should compare current values with a recent baseline and identify pipeline version changes.

## Analysis and statistics questions

### 49. Why report medians and IQRs instead of means?

Activity and entropy-related distributions can be skewed and contain highly active users. Medians and interquartile ranges describe the typical user and spread without letting extreme values dominate. I still inspect full distributions rather than relying on one summary.

### 50. Is the 0.007 city-median difference meaningful?

I would not treat it as a meaningful city ranking. The distributions overlap heavily, and sampling, Foursquare adoption, category taxonomy, and user composition could explain such a small descriptive difference. Practical importance and representativeness matter more than whether a large sample produces a small p-value.

### 51. Can you conclude that Tokyo users explore more than NYC users?

No. The dataset contains selected Foursquare users and voluntary check-ins, not representative city populations or complete movement. The safe statement is that the two historical samples have similar median normalized venue entropy.

### 52. Why compare weekday and weekend within the same user?

A paired comparison controls for stable differences between users, such as their overall activity volume and check-in habits. I calculate each eligible user's weekend-minus-weekday entropy and summarize those differences. Comparing unrelated weekday and weekend groups would mix context with user composition.

### 53. Why require at least 20 check-ins in each context?

Entropy from very small samples is unstable. The threshold removes the sparsest weekday or weekend histories before making a paired comparison. It is a pragmatic rule, not a theoretically proven cutoff, and it should be tested with sensitivity analysis.

### 54. How could changing the 20-check-in threshold affect the result?

A lower threshold includes more users but adds noisier entropy estimates. A higher threshold improves per-context support but excludes more users and may overrepresent very active users. I would plot the median delta, positive share, uncertainty, and eligible population over several thresholds.

### 55. Should you perform a significance test?

A paired bootstrap interval or paired nonparametric test could quantify uncertainty in the median weekend difference. A permutation or bootstrap analysis could also examine the city gap. However, statistical significance would not fix selection bias, incomplete check-ins, or lack of practical importance. The current solution emphasizes descriptive distributions and claim boundaries.

### 56. Why does correlation not mean venue and category entropy are the same?

They can move together because visiting more venues often exposes more categories, but they encode different units. A user may visit many venues within one category. Rank correlations were 0.897 in NYC and 0.728 in Tokyo, which shows association but also meaningful differences, especially in Tokyo.

### 57. What biases exist in voluntary Foursquare check-ins?

Users choose whether, when, and where to check in. Check-ins may overrepresent social, public, or interesting venues and underrepresent routine or sensitive locations. Foursquare users are also not representative of city residents. The dataset measures recorded platform behavior, not complete mobility or demand.

### 58. Could more active users appear systematically different?

Yes. More observations reveal more rare venues and may change both raw and normalized entropy estimates. Activity may also correlate with platform engagement or user type. That is why the analysis reports observation and unique-venue counts alongside entropy and checks their relationships.

### 59. How would you measure uncertainty in each user's entropy?

I could bootstrap that user's check-ins to estimate an interval, use repeated subsampling to measure stability by history length, or apply a bias-corrected entropy estimator. For a product, I would turn stability and sample size into a calibrated confidence measure rather than relying on a hand-designed confidence value.

### 60. How would you test whether findings generalize to current users?

I would use recent, consented data from the intended product population, reproduce the metric with the same definitions, inspect coverage and subgroup stability, and test findings on a later holdout period. Current data is essential because the source check-ins are from 2012 to 2013.

## Product questions

### 61. How did you move from an observation to a product hypothesis?

I separated evidence from interpretation. The data shows user variation, a weekend pattern, and a distinction between venue and category diversity. I then asked whether those signals could support cautious recommendation controls. That produced a testable hypothesis, not a claim that the feature already works.

### 62. Why choose Context-Aware Discovery?

It connects the main findings without relying on city stereotypes. It can keep explicit preference in control, use context only when confidence is adequate, and expose its reasoning. It is also testable against a baseline ranker using the same candidate pool.

### 63. Does the analysis prove high-entropy users want novel recommendations?

No. The data contains check-ins but no recommendation impressions, choices, saves, or satisfaction outcomes. Entropy describes past distributions. Preference for recommendation novelty is a separate behavioral question that requires an experiment.

### 64. What does "new" mean in the prototype?

It means either less commonly visited in this historical sample or a category absent from the selected synthetic profile's familiar categories. It does not mean newly opened, currently operating, higher quality, or suitable for a real trip.

### 65. What is the difference between profile entropy and candidate novelty?

Profile entropy describes the diversity of a synthetic profile's observed history. Candidate novelty is the inverse of a candidate's aggregate popularity percentile in the historical sample. They belong to different entities and must not be described as the same score. No venue receives an entropy score.

### 66. What is category familiarity?

It is a binary signal showing whether a candidate's category appears in the selected synthetic profile's familiar-category list. It is separate from aggregate candidate novelty. A venue can be historically uncommon but belong to a familiar category, or common but belong to an unfamiliar category.

### 67. Why does explicit preference receive the strongest weight?

A user's current declared choice is stronger evidence of intent than an inference from incomplete historical check-ins. In the illustrative policy, explicit mode contributes 70 percent of applied discovery and the confidence-adjusted profile signal contributes 30 percent. These weights are hand-designed and require calibration.

### 68. How does the system handle sparse histories?

If profile confidence is below 0.50, the inferred profile signal falls back to neutral at 0.50 and the weekend adjustment is disabled. The explicit user choice remains active. This avoids strong personalization from a very small history.

### 69. Why are the ranking weights hand-designed?

There are no recommendation outcome labels in the dataset. Learned weights would pretend that the project had evidence it does not possess. Hand-designed weights make the prototype's behavior inspectable, but they are implementation assumptions rather than validated parameters.

### 70. Why build a deterministic prototype instead of training a model?

The goal was to demonstrate the product behavior and make the hypothesis testable. Deterministic rules provide stable, explainable outputs without claiming learned relevance. A real model should only be trained after obtaining suitable impression and outcome data.

### 71. What data would you need for a real recommender?

I would need timestamped recommendation impressions, candidate sets, rank positions, user selections or saves, dismissals, repeat engagement, context, availability, distance, and privacy-safe profile features. Training and evaluation would need time-based splits and protection against position bias and leakage.

### 72. How would you evaluate whether the feature works?

I would run a randomized experiment over the same eligible candidate pool. The control would use baseline relevance ranking. The treatment would apply the context-aware policy with the same explicit override. I would compare user outcomes and guardrails rather than offline entropy alone.

### 73. What would the control and treatment groups be?

Control uses the existing or popularity-based baseline ranker. Treatment uses context-aware novelty adjustment. Both groups should have the same candidate eligibility rules, interface, and explicit user controls so the ranking policy is the main difference.

### 74. What primary metric would you select?

The proposed primary metric is save or selection rate per recommendation impression. It directly measures whether shown recommendations produce the intended immediate action. I would define the event and attribution window before starting the experiment.

### 75. What guardrail metrics would you monitor?

I would monitor hides and dismissals, early exits, repeated suggestions, travel distance, latency, sparse-history performance, subgroup effects, and user-control usage. Return engagement and catalog coverage can be useful secondary metrics, but they should not hide a worse immediate experience.

## Prototype and privacy questions

### 76. Why use synthetic profiles instead of actual users?

The prototype only needs representative states to demonstrate ranking behavior. Synthetic profiles avoid exposing or re-identifying source users and prevent the interface from implying that a historical person's behavior is current. They also make edge cases such as sparse history easy to test.

### 77. How are candidate venues generated?

An offline script groups real historical venue records, excludes sensitive categories, and requires at least 30 check-ins and 15 distinct visitors. It selects eight eligible candidates per city across the popularity range. It then rounds support counts and emits only safe aggregate fields.

### 78. Why are candidate names pseudonymous?

The source data contains venue IDs but no proper venue names. Inventing names would fabricate information, while exposing source IDs would weaken privacy minimization. Labels such as `NYC · Coffee Shop · Candidate 08` describe the known city and category honestly.

### 79. Which fields are excluded from the browser and API?

The safe catalog excludes source user IDs, source venue IDs, exact coordinates, timestamps, trajectories, and private-home details. The API exposes generated IDs, pseudonymous labels, city, category, rounded support, popularity, novelty, and provenance.

### 80. Why exclude homes, offices, and residential categories?

These categories are sensitive and inappropriate for venue discovery. Excluding them reduces privacy and safety risk. The exclusion is applied before the candidate catalog is generated, so the API never receives those candidates.

### 81. Could the historical candidates still exist today?

Possibly, but the prototype does not know. The records are from 2012 to 2013 and have no live business information. The interface therefore describes them as historical candidates, not a current place guide.

### 82. Is candidate popularity the same as relevance?

No. Popularity is an aggregate historical signal. The prototype transforms it into an illustrative baseline relevance score because no true user-level relevance model exists. Real relevance would require current context, availability, distance, preferences, quality, and outcome data.

### 83. Is this a machine-learning recommender?

No. It is a deterministic ranking prototype with hand-designed formulas. It demonstrates how controls and signals might interact, but it has not learned parameters or been validated against recommendation outcomes.

### 84. How does the sparse-history fallback work?

Profiles with confidence below 0.50 receive a neutral inferred discovery value of 0.50. They get no weekend adjustment. Applied discovery therefore depends mainly on explicit mode, and the API returns a clear limited-history explanation.

### 85. How would you stop unsuitable repeated recommendations?

A production system would need impression history, dismissals, frequency caps, availability, distance constraints, diversity controls, and safety filters. The historical prototype has no persistence, so it cannot solve repeated exposure or live suitability.

### 86. What privacy review would be needed before launch?

I would require purpose limitation, consent or another valid basis, retention limits, deletion controls, access restrictions, aggregation rules, re-identification risk assessment, and review of inferred home or work signals. I would also test whether personalization creates differential harm across user groups.

## Harder challenge questions

### 87. Could duplicate removal remove legitimate repeated check-ins?

It is possible that two genuinely separate events are identical across every source field, including timestamp, but the data cannot distinguish them. Exact matching is the narrowest defensible deduplication rule. Broader rules would erase legitimate repeat visits, while keeping exact replays would bias counts.

### 88. Does normalization really make users comparable?

Only partly. It places evenness on a common 0-to-1 scale relative to each user's observed venue set. It does not equalize unique venue count, observation duration, sample size, missing check-ins, or platform behavior. Comparisons still need supporting counts and uncertainty.

### 89. Could category taxonomy differences explain the city result?

Yes, especially for category entropy. The cities may differ in category coverage, metadata quality, and venue labeling. That is one reason I treat the comparison as descriptive and avoid cultural explanations.

### 90. Is weekend entropy higher because weekend check-ins are recorded differently?

That is plausible. People may be more likely to record social or unusual weekend activities. The paired design reduces differences between users but cannot remove context-dependent reporting behavior. The finding is about recorded check-ins, not proven movement behavior.

### 91. Could using the full historical dataset create time leakage?

Yes, in a real recommender. Popularity or profile features must be computed only from events available before each recommendation time. The prototype is a static historical demonstration, not an offline predictive evaluation, but a production pipeline would require time-aware feature snapshots.

### 92. How would you avoid future-data leakage when calculating popularity?

I would calculate rolling popularity using only events before the recommendation timestamp, with a defined lookback window and delayed-event policy. Training and evaluation would use chronological splits, and feature generation would be reproducible as of each event time.

### 93. Why did you not add confidence intervals or threshold sensitivity analysis?

The current submission prioritizes a clear descriptive analysis and production-oriented metric implementation. This remains a weakness. My first statistical improvement would be a paired bootstrap for weekend deltas and a sensitivity analysis across context thresholds and history lengths.

### 94. What is the weakest part of the solution?

The product ranking policy has no behavioral outcome evidence. Its confidence values, weights, sparse threshold, and scoring curve are hand-designed. Also, the source data is old and selected. The prototype shows inspectable implementation, not recommendation effectiveness.

### 95. If you had one more week, what would you improve?

First, I would quantify entropy stability by history length and test the 20-event threshold. Second, I would add confidence intervals and time-aware robustness checks. For product work, I would specify a current-data experiment and calibrated confidence policy before attempting a more complex model.

### 96. What if discovery increases but dismissals also increase?

I would examine the pre-defined tradeoff and segment results by explicit mode, confidence, context, and baseline entropy. More discovery is not automatically better. I would reduce or constrain the adjustment, improve candidate eligibility, or limit it to users who explicitly request novelty if user experience worsens.

## Exact prototype formulas

These are useful for technical follow-up questions. They are illustrative rules, not learned parameters.

### Inferred profile discovery

\[
D_{inferred}=0.60H_{venue}+0.40H_{category}
\]

For reliable profiles, confidence blends this with neutral:

\[
D_{adjusted}=cD_{inferred}+(1-c)0.50
\]

For confidence below 0.50, the adjusted value is set to 0.50.

### Applied discovery

Explicit modes map to:

- Familiar: 0.20
- Balanced: 0.50
- Something new: 0.80

Then:

\[
D_{applied}=0.70D_{explicit}+0.30D_{adjusted}+context\ adjustment
\]

A reliable weekend profile receives:

\[
context\ adjustment=c\times weekend\ delta
\]

The final result is clipped to the range 0 to 1.

### Candidate scoring

Category discovery is 1 for a category absent from the profile history and 0 for a familiar category:

\[
N_{candidate}=0.65N_{aggregate}+0.35D_{category}
\]

The novelty weight is:

\[
w=D_{applied}^{1.5}
\]

The final candidate score is:

\[
score=(1-w)\times baseline\ relevance+w\times N_{candidate}
\]

Candidates are sorted using the exact unrounded score. Generated candidate ID breaks true ties.

## Numbers to memorize

| Measure | NYC | Tokyo |
|---|---:|---:|
| Raw rows | 227,428 | 573,703 |
| Exact duplicates | 250 | 577 |
| Clean rows | 227,178 | 573,126 |
| Users | 1,083 | 2,293 |
| Venues | 38,333 | 61,858 |
| Median check-ins | 153 | 173 |
| Median unique venues | 76 | 80 |
| Median normalized venue entropy | 0.853 | 0.860 |
| Median normalized category entropy | 0.810 | 0.707 |
| Eligible weekday/weekend users | 1,019 | 2,142 |
| Median weekend-minus-weekday entropy | 0.058 | 0.059 |
| Share with positive weekend difference | 88.5% | 85.4% |
| Inconsistent timezone-offset rows | 456 | 27 |

## Statements to avoid

Do not say:

- "The surprise factor is the number of check-ins."
- "High entropy means adventurous."
- "Tokyo users explore more."
- "Weekends cause exploration."
- "A venue has an entropy score."
- "Novelty means newly opened."
- "The prototype is a trained recommender."
- "Historical popularity is true relevance."
- "The dataset represents everyone in NYC and Tokyo."

Prefer:

> The analysis describes how evenly each user's recorded check-ins are distributed. It motivates a recommendation hypothesis, but recommendation outcomes still require a randomized experiment.
