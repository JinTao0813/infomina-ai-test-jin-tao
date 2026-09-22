# Teaching notes

- This guide prepares me to discuss the existing solution rather than rebuild it.
- Refreshed against the current repository: the solution now includes a generated analysis site and a full-stack deterministic Discovery Mode prototype.
- Entropy was new to me when I started, so explanations should begin with the idea before introducing shorthand.
- Prefer concrete code paths, exact findings, honest tradeoffs, and answers I could naturally say aloud.
- Keep the core metric contract exact: `calculate_location_entropy(data, group_cols, location_col)`. It has no weight or configurable-log-base argument.
- Keep profile entropy separate from candidate novelty and category familiarity. Never say a venue has entropy.
- Describe candidate labels as pseudonymous and data-derived, profiles as synthetic, and ranking weights as hand-designed—not learned.
- Keep all teaching material under `teach/`.
- Do not assume that reading a lesson means I understand it. Use recall prompts and self-grading to find gaps.
