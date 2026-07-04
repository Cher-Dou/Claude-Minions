---
description: Run a systematic literature scout on a topic and produce a screened evidence table.
---

Use the **lit-scout** agent to run a systematic literature search on: **$ARGUMENTS**

Frame the question in PECO, build a reproducible Boolean query with the `pubmed-search` skill, retrieve and deduplicate records, screen title/abstract against explicit criteria, and produce an evidence table plus a screening log. Save all outputs to files. Do not fabricate any citation.
