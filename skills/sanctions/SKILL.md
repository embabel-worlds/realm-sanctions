---
name: sanctions
description: Screen tracked parties against consolidated sanctions lists (OFAC SDN and the wider set). Use for "is any counterparty/customer/supplier sanctioned", "sanctions check", "are we clear", "who matched the list". Reports exact and official-alias matches only, keyless — not fuzzy or PEP screening.
---

# Sanctions screening, and its limits

Screens the parties this world tracks against the consolidated sanctions lists,
held as `ScreenResult` rows.

| The question | The view |
|---|---|
| Full screen, exceptions first | `SanctionsScreen` |
| Just the matches | `SanctionsHits` |

## Say it honestly

- **`clear` means "no exact or official-alias match"**, never "cleared by a
  compliance officer". Say it that way.
- **Matching is exact + alias, not fuzzy.** A transliteration or near-miss will
  read as clear. For fuzzy and PEP screening, the realm needs an OpenSanctions
  key; this is the keyless first pass.
- **A `hit` is a name/alias match, not proof of identity.** Two entities can
  share a name — a hit is a flag to investigate, not a verdict.
