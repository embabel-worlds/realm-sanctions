# realm-sanctions

**When to run it.** Screen the parties you already track — CRM accounts,
counterparties, suppliers, donors — against the consolidated sanctions lists.
The one counterparty check with legal teeth, joinable to the rest of your world
on the party's name.

```
ScreenResult   one row per party: hit | clear, with matched entry, programme, country
```

## Source

The authoritative lists are published as **open bulk data, keyless**:

- **OFAC SDN** — `https://data.opensanctions.org/datasets/latest/us_ofac_sdn/entities.ftm.json`
  (~72k entities, with names, aliases, topics, programmes, countries)

No account, no key. OpenSanctions also publishes the wider consolidated set the
same way; point `scripts/screen.py` at another dataset to widen coverage.

## How it works, and its limits — read this

There is **no keyless per-name search API** for sanctions (OpenSanctions' live
`/search` and `/match` require a key; OFAC's endpoint only returns the full
50 MB list). So this realm does not fetch per-anchor at query time. Instead:

1. `scripts/screen.py` downloads the list once and screens a set of party names.
2. Each result is written as a `ScreenResult` row.
3. The views read those rows.

Matching is **exact + official-alias only** — not fuzzy, not transliteration.
A `clear` result means *"no exact or alias match on the list"*, **never** a
compliance sign-off, and a near-miss (a transliterated spelling, a slightly
different legal name) will read as clear. A `hit` is a name/alias match, a flag
to investigate, not a proof of identity — two entities can share a name.

**For fuzzy + PEP + live screening**, rebuild the producer on the OpenSanctions
`/match` API: set `OPENSANCTIONS_API_KEY` and declare the api with
`auth: bearer, token-env: OPENSANCTIONS_API_KEY`. That is the paid/keyed upgrade;
this realm is the honest keyless first pass.

## Populate it

```bash
# 1. screen your parties (one name per line) → ScreenResult rows as JSON
printf 'Atlassian\nRosneft\n' | python3 scripts/screen.py > rows.json

# 2. load them (via the appliance code surface)
#    gateway.repository.createEntries({ type: "ScreenResult", rows: <rows.json> })
```

Then run `SanctionsScreen` (exceptions first) or `SanctionsHits`.

## Licence

Apache 2.0. Sanctions data © the issuing authorities, via OpenSanctions' open
bulk distribution, used under its terms.
