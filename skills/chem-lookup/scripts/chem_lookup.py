#!/usr/bin/env python3
"""Resolve chemical identity + properties from PubChem (and optionally EPA CompTox).

Usage:
    python chem_lookup.py "bisphenol A" --out results/chem
    python chem_lookup.py --cas 80-05-7 --out results/chem
    python chem_lookup.py --smiles "CC(C)(c1ccc(O)cc1)c1ccc(O)cc1" --out results/chem

No API key required for PubChem. Outputs <out>_profile.json.
"""
import argparse
import json
import os
import sys

try:
    import requests
except ImportError:
    sys.exit("Missing dependency: pip install requests")

PUG = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
PROPS = "MolecularFormula,MolecularWeight,SMILES,ConnectivitySMILES,InChIKey,XLogP,IUPACName"
CCTE = "https://api-ccte.epa.gov"


def _get(url, params=None):
    r = requests.get(url, params=params, timeout=30,
                     headers={"User-Agent": "claud-minions-toxprofiler"})
    r.raise_for_status()
    return r.json()


def resolve_cids(name=None, cas=None, smiles=None):
    if smiles:
        data = _get(f"{PUG}/compound/smiles/{requests.utils.quote(smiles)}/cids/JSON")
    elif cas:
        data = _get(f"{PUG}/compound/name/{requests.utils.quote(cas)}/cids/JSON")
    else:
        data = _get(f"{PUG}/compound/name/{requests.utils.quote(name)}/cids/JSON")
    return data.get("IdentifierList", {}).get("CID", [])


def fetch_properties(cid):
    data = _get(f"{PUG}/compound/cid/{cid}/property/{PROPS}/JSON")
    props = data.get("PropertyTable", {}).get("Properties", [{}])
    return props[0] if props else {}


def fetch_synonyms(cid, limit=12):
    try:
        data = _get(f"{PUG}/compound/cid/{cid}/synonyms/JSON")
        syns = data.get("InformationList", {}).get("Information", [{}])[0].get("Synonym", [])
    except Exception:
        return [], None
    # Heuristic CAS: pattern digits-digits-digit
    cas = None
    for s in syns:
        parts = s.split("-")
        if len(parts) == 3 and all(p.isdigit() for p in parts) and len(parts[2]) == 1:
            cas = s
            break
    return syns[:limit], cas


def fetch_comptox(query, api_key):
    """Resolve DTXSID + summarize ToxCast/bioactivity via EPA CCTE APIs.

    Best-effort: CCTE endpoints require a free API key. Any failure returns a
    note instead of raising, so identity lookup still succeeds.
    """
    if not api_key:
        return {
            "available": False,
            "note": "No EPA CCTE API key provided (set --ccte-key or CCTE_API_KEY). "
                    "Get a free key at https://api-ccte.epa.gov/docs/. Skipping bioactivity.",
        }
    headers = {"x-api-key": api_key, "accept": "application/json",
               "User-Agent": "claud-minions-toxprofiler"}
    try:
        r = requests.get(f"{CCTE}/chemical/search/equal/{requests.utils.quote(query)}",
                         headers=headers, timeout=30)
        r.raise_for_status()
        hits = r.json()
        if not hits:
            return {"available": True, "note": f"No CompTox chemical matched '{query}'."}
        dtxsid = hits[0].get("dtxsid")
    except Exception as e:  # noqa: BLE001 - degrade gracefully on any API error
        return {"available": False, "note": f"CompTox identity lookup failed: {e}"}

    result = {"available": True, "dtxsid": dtxsid,
              "source": f"EPA CompTox {dtxsid} (https://comptox.epa.gov/dashboard/chemical/details/{dtxsid})"}
    try:
        b = requests.get(f"{CCTE}/bioactivity/data/summary/search/by-dtxsid/{dtxsid}",
                         headers=headers, timeout=30)
        b.raise_for_status()
        summary = b.json()
        if isinstance(summary, list):
            total = len(summary)
            active = sum(1 for a in summary if str(a.get("hitc", "")).startswith("1")
                         or a.get("hitcall", 0) and float(a.get("hitcall", 0)) >= 0.5)
            result["toxcast_assays_tested"] = total
            result["toxcast_assays_active"] = active
            result["note"] = ("ToxCast 'active' = in vitro assay signal, NOT evidence of human harm.")
    except Exception as e:  # noqa: BLE001
        result["bioactivity_note"] = f"Bioactivity summary unavailable: {e}"
    return result


def main():
    ap = argparse.ArgumentParser(description="Chemical identity + properties via PubChem.")
    ap.add_argument("name", nargs="?", default=None)
    ap.add_argument("--cas", default=None)
    ap.add_argument("--smiles", default=None)
    ap.add_argument("--ccte-key", default=os.environ.get("CCTE_API_KEY"),
                    help="EPA CCTE API key for CompTox/ToxCast bioactivity (or set CCTE_API_KEY).")
    ap.add_argument("--out", default="chem")
    args = ap.parse_args()

    if not (args.name or args.cas or args.smiles):
        sys.exit("Provide a name (positional), --cas, or --smiles.")

    query_desc = args.smiles and f"SMILES={args.smiles}" or args.cas and f"CAS={args.cas}" or f"name={args.name}"

    try:
        cids = resolve_cids(name=args.name, cas=args.cas, smiles=args.smiles)
    except requests.HTTPError as e:
        sys.exit(f"PubChem lookup failed for {query_desc}: {e}")

    if not cids:
        sys.exit(f"No PubChem record found for {query_desc}.")

    ambiguous = len(cids) > 1
    cid = cids[0]
    props = fetch_properties(cid)
    synonyms, cas = fetch_synonyms(cid)

    profile = {
        "query": query_desc,
        "pubchem_cid": cid,
        "ambiguous_match": ambiguous,
        "all_cids": cids[:10],
        "cas_rn": cas or (args.cas if args.cas else None),
        "iupac_name": props.get("IUPACName"),
        "molecular_formula": props.get("MolecularFormula"),
        "molecular_weight": props.get("MolecularWeight"),
        "smiles": props.get("SMILES"),
        "connectivity_smiles": props.get("ConnectivitySMILES"),
        "inchikey": props.get("InChIKey"),
        "xlogp_predicted": props.get("XLogP"),
        "synonyms": synonyms,
        "sources": {
            "identity_properties": f"PubChem CID {cid} (https://pubchem.ncbi.nlm.nih.gov/compound/{cid})",
        },
        "notes": [],
    }

    # EPA CompTox / ToxCast bioactivity (best-effort; needs a free API key)
    comptox_query = profile["cas_rn"] or args.name or args.smiles
    profile["comptox"] = fetch_comptox(comptox_query, args.ccte_key)
    if profile["comptox"].get("source"):
        profile["sources"]["bioactivity"] = profile["comptox"]["source"]
    if ambiguous:
        profile["notes"].append(f"Query matched {len(cids)} CIDs; using {cid}. Disambiguate before relying on this.")
    if props.get("XLogP") is not None:
        profile["notes"].append("XLogP is a computed (predicted) value, not experimental.")

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    out_path = f"{args.out}_profile.json"
    with open(out_path, "w") as f:
        json.dump(profile, f, indent=2)

    print(json.dumps(profile, indent=2))
    print(f"\nSaved profile -> {out_path}")
    if profile["notes"]:
        print("\nNOTES:")
        for n in profile["notes"]:
            print(f"  - {n}")


if __name__ == "__main__":
    main()
