---
description: Produce a daily literature update on EDCs/MDCs and nutrient-based protection.
---

Use the **lit-scout** agent to collect the most recent peer-reviewed studies and authoritative reviews on endocrine-disrupting chemicals (EDCs), metabolic disrupting chemicals (MDCs), and natural nutrients or dietary compounds that may protect against EDC/MDC-related detrimental health effects.

Scope the update to: **$ARGUMENTS**

If no narrower scope is provided, use this default scope:
**EDCs and MDCs linked to metabolic disease, obesity, insulin resistance, MASLD/MASH, reproductive-metabolic dysfunction, oxidative stress, inflammation, mitochondrial dysfunction, gut microbiome disruption, and nutrient or natural-compound interventions.**

Prioritize:
1. Primary studies from the last 12 months.
2. Human biomonitoring, cohort, clinical, or intervention evidence when available.
3. Animal and in vitro mechanistic evidence, clearly labeled.
4. Recent high-quality reviews only when they clarify mechanisms or evidence gaps.

Use the `pubmed-search` skill to run a reproducible search. Include terms such as:
`endocrine disrupting chemicals`, `metabolic disrupting chemicals`, `obesogens`, `bisphenol`, `phthalate`, `PFAS`, `microplastics`, `insulin resistance`, `obesity`, `MASLD`, `oxidative stress`, `inflammation`, `mitochondrial dysfunction`, `gut microbiome`, `quercetin`, `resveratrol`, `curcumin`, `anthocyanins`, `astaxanthin`, `selenium`, `vitamin`, `polyphenols`, `probiotics`, and `dietary intervention`.

Return the daily update as a concise Markdown table with these columns:

| Date | Topic | Chemical/exposure | Nutrient/intervention | Study type/model | Key findings | Health relevance | Limitations | Link/DOI |
|---|---|---|---|---|---|---|---|---|

After the table, add:
- **Main takeaways**: 3-5 concise bullets.
- **Evidence balance**: clearly separate human evidence from animal/in vitro evidence.
- **Practical implications**: exposure-reduction or dietary resilience signals supported by the retrieved evidence.

Rules:
- Do not fabricate citations, PMIDs, DOIs, study designs, or effect sizes.
- Link every included study to PubMed, Europe PMC, DOI, or the publisher page.
- Flag online-ahead records whose journal issue date is in the future.
- Avoid medical advice; describe evidence strength and uncertainty.
