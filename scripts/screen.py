#!/usr/bin/env python3
"""Screen party names against the live OFAC SDN list, keyless.

Reads party names from stdin (one per line, optionally `name<TAB>role`) and
emits ScreenResult rows as JSON on stdout, ready for
`gateway.repository.createEntries({type: "ScreenResult", rows})`.

    printf 'Atlassian\nRosneft\n' | python3 scripts/screen.py > rows.json

Matching is EXACT + official-alias, case-insensitive — not fuzzy. A `clear` is
the absence of an exact/alias match, not a human clearance. See the README.
"""
import json, sys, urllib.request

INDEX_URL = "https://data.opensanctions.org/datasets/latest/us_ofac_sdn/entities.ftm.json"
LIST_NAME = "OFAC SDN"


def load_index():
    """Return {lower(name|alias): (via, display, schema, topics, country, program, sourceUrl)}."""
    # The dataset URL 307-redirects to a dated artifact; urllib follows it.
    req = urllib.request.Request(INDEX_URL, headers={"User-Agent": "realm-sanctions"})
    idx, n = {}, 0
    with urllib.request.urlopen(req, timeout=120) as r:
        for line in r:
            line = line.strip()
            if not line:
                continue
            e = json.loads(line)
            p = e.get("properties", {})
            disp = (p.get("name") or ["?"])[0]
            meta = (disp, e.get("schema"), ",".join(p.get("topics") or []),
                    ",".join(p.get("country") or []),
                    ",".join(p.get("programId") or p.get("program") or []),
                    (p.get("sourceUrl") or [""])[0])
            for nm in (p.get("name") or []):
                idx.setdefault(nm.strip().lower(), ("name",) + meta)
            for al in (p.get("alias") or []):
                idx.setdefault(al.strip().lower(), ("alias",) + meta)
            n += 1
    return idx, n


def main():
    idx, size = load_index()
    today = sys.argv[1] if len(sys.argv) > 1 else ""  # pass an ISO date; scripts can't read the clock deterministically
    rows = []
    for raw in sys.stdin:
        raw = raw.rstrip("\n")
        if not raw.strip():
            continue
        party, _, role = raw.partition("\t")
        party = party.strip()
        hit = idx.get(party.lower())
        if hit:
            via, disp, schema, topics, country, prog, src = hit
            rows.append({"party": party, "role": role.strip(), "status": "hit",
                         "matchedName": disp, "matchedVia": via, "listName": LIST_NAME,
                         "program": prog, "country": country, "schemaType": schema,
                         "sourceUrl": src, "screenedOn": today, "listSize": str(size)})
        else:
            rows.append({"party": party, "role": role.strip(), "status": "clear",
                         "matchedName": "", "matchedVia": "", "listName": LIST_NAME,
                         "program": "", "country": "", "schemaType": "",
                         "sourceUrl": "", "screenedOn": today, "listSize": str(size)})
    json.dump(rows, sys.stdout, indent=2)
    print(f"\n# screened {len(rows)} parties against {size} {LIST_NAME} entities", file=sys.stderr)


if __name__ == "__main__":
    main()
