# Structural contract audit

All 950 declared property/end records, with metadata reference/bounds checks and explicit evidence scopes. Association-owned ends have no generated direct setters and are not counted in stored-setter sweeps.

| Definition kind | Count |
| --- | --- |
| structural property | 549 |
| derived property | 73 |
| association-owned property | 328 |

The 549 stored declarations receive default/wrong-type and declared-type assignment sweeps. Metadata diagnostics: 0.

Family examples cover uniqueness/order/bags, bounds, composites, inverse rebinding, subset witnesses, stored redefinitions, rollback, derived-write protection, cross-session links and cached collections after deletion.

Cross-session references remain allowed and transactionally updated/cleaned. validate reports cross session reference on stored links; allInstances-based queries remain scoped to each element extent.

Selected version-specific boundary grids, edit sequences and independent adapted interchange are documented in [CONFORMANCE_MATRIX.md](CONFORMANCE_MATRIX.md). These do not turn the declaration sweeps into exhaustive behavioral evidence.

Detailed per-definition links and their evidence scope are in `structural-audit.json`. Regenerate with `python structural_audit.py`.

Per-association/end behavior, all positive subtype/default combinations, arbitrary mutation sequences, broader normative prose and a complete XMI/serialization contract remain open.
