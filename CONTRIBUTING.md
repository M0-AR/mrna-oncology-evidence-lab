# Contributing

Thanks for helping improve the audit. This repository is designed to be corrected in public, with evidence.

## Ground rules

1. **Do not hand-edit generated evidence.** Change the source, config, or code, then rebuild.
2. **Every claim needs a source.** Add or update a source record, commit a snapshot where legally possible, record its SHA-256, and write an evidence note.
3. **Preserve the verdict schema.** Use `supported`, `partially_supported`, `unsupported`, or `not_verifiable`.
4. **Supported is not true.** A claim can faithfully match an official statement even when the underlying science is contested. Keep that distinction explicit.
5. **Separate clinical, market, and financial claims.** Do not let a price move become an efficacy claim.
6. **Do not add paywalled text, personal data, or medical advice.**
7. **Keep the static site dependency-free.** No external JavaScript, CSS, or font frameworks.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
make all
```

`make all` runs the pipeline, regenerates the site data bundle, runs the test suite, and verifies manifests and numerical invariants.

To preview the site:

```bash
python -m http.server 8000
# open http://localhost:8000/preview.html
```

## Evidence changes

When adding or changing a claim:

1. Update `config/claims.yaml`.
2. Add or update the source in `config/sources.yaml`.
3. Add the snapshot under `evidence/snapshots/` if the source terms permit it.
4. Rebuild so `results/tables/claims.csv` and `assets/site-data.js` regenerate.
5. Confirm `python scripts/verify.py` passes.
6. Explain the evidence and the verdict in the pull request.

If a source cannot be snapshotted, mark it clearly and explain why. A paywall is a limitation, not a reason to hide the source.

## Pull request checklist

- [ ] `make all` passes.
- [ ] `python scripts/verify.py` passes.
- [ ] New/changed claims have source IDs and evidence notes.
- [ ] No generated file was edited by hand.
- [ ] No secrets, personal data, or paywalled source text were added.
- [ ] The site still works at desktop and mobile widths.
- [ ] The README and preview use the same numbers.
- [ ] The change does not turn the project into medical or investment advice.

## Reporting a correction

Open an issue with:

- the claim ID (`C01`–`C42`);
- the exact wording that is wrong;
- the source ID and snapshot;
- the proposed correction and its evidence.

Corrections are welcome. The goal is not to defend the ledger; it is to make the ledger more accurate.
