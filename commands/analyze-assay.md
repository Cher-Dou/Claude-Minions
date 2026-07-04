---
description: QC, normalize, and dose-response fit an in vitro plate dataset.
---

Use the **bioassay-analyst** agent on the assay data at: **$ARGUMENTS**

First confirm the plate layout and control roles. Run QC with the `assay-qc` skill (Z'-factor, control CV, outliers) and state the verdict. Normalize to controls, then fit a dose-response curve with the `dose-response-fitting` skill, reporting EC50/IC50 with 95% CI, Hill slope, and R². Plot with the `pub-figures` skill. Do not report an EC50 without its CI and R², and flag any extrapolation.
