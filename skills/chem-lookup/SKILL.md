---
name: chem-lookup
description: Resolve chemical identity and pull physicochemical + bioactivity data from PubChem and the EPA CompTox Chemicals Dashboard. Use to convert between name/CAS/SMILES/InChIKey and to retrieve properties or ToxCast assay activity. Provides a ready-to-run Python script (no API key required).
---

# Chemical lookup (PubChem + EPA CompTox)

Resolves a chemical to a trustworthy identity and pulls key data.

## When to use
Whenever a compound needs an authoritative CAS/SMILES/InChIKey, physchem properties, or in vitro bioactivity context.

## APIs used (no key required)
- **PubChem PUG-REST** (`https://pubchem.ncbi.nlm.nih.gov/rest/pug`) — identity + properties.
- **EPA CompTox / CCTE APIs** (`https://api-ccte.epa.gov`) — DTXSID resolution and ToxCast/bioactivity. Some CCTE endpoints prefer an API key (free); the script degrades gracefully to identity-only if unavailable.

## Quick start
```bash
python scripts/chem_lookup.py "bisphenol A" --out results/chem
# or by CAS / SMILES:
python scripts/chem_lookup.py --cas 80-05-7 --out results/chem
python scripts/chem_lookup.py --smiles "CC(C)(c1ccc(O)cc1)c1ccc(O)cc1" --out results/chem
```

Outputs:
- `results/chem_profile.json` — CID, CAS, InChIKey, canonical SMILES, formula, MW, XLogP, name synonyms
- prints a readable summary

## Reporting rules (enforce these)
- Always report the identifier you queried with and the resolved CID/DTXSID — enables anyone to reproduce.
- Flag ambiguity: isomers, salts vs free acid, mixtures. If a name maps to multiple CIDs, stop and disambiguate.
- Mark predicted vs experimental properties (PubChem XLogP is computed).
- A ToxCast assay "hit" is an in vitro signal, not proof of human harm — never state it as toxicity.

## Dependencies
`requests`. Install: `pip install requests`
