# Classification and StructuredClassifiers behavioral evidence

This increment adds explicit expected outcomes for both UML 2.4.1 and 2.5.1.
It does not certify the whole specification. The existing structural inventory,
native implementation inventory and public XMI corpus remain separate evidence.

## Sources and interpretation

The normative machine-readable sources are vendored in `umltools/data/UML-2.4.1.xmi`
and `umltools/data/UML.xmi`. Their upstream URLs and SHA-256 digests are recorded
in `scripts/uml-version-sources.json`. The anchors below are source identifiers,
not implementation function names used to calculate expected results.

| Source anchor / contract | Authored oracle | Evidence for each version |
| --- | --- | --- |
| Property-isConsistentWith | Redefining type must conform, lower bound cannot decrease, upper bound cannot increase; composite redefinee requires composite redefiner | 180 combinations: lower 0/1/2/4, upper 2/4/5/unlimited, same/sub/unrelated type, both aggregation flags; malformed intervals excluded |
| Property-isCompatibleWith | Same type, Property versus Port metaclass direction | Two explicit directed results |
| Property-opposite, Property-isNavigable | Binary ends, classifier/association ownership, navigable-owned membership | Eight ownership/navigation combinations, then third-end mutation |
| Classifier-allParents, Classifier-inheritedMember | Diamond ancestor identity, one inherited public member, exclusion of private member | Remove each branch, reattach, clear required reference, repair |
| Generalization-general | Missing general is a multiplicity violation; dependent evaluations cannot succeed | Structured diagnostics before and after repair |
| Property-subsetting_rules/context_conforms/subsetted_property_names | Type conformance and upper bound restriction; lower bound is not restricted by this rule | 24 combinations, context removal/repair and duplicate-name removal/repair |
| Connector-types/roles | Each role type conforms to corresponding association-end type; arity and owner membership required | Nine type pairs, missing role, arity mismatch and removed role, each repaired |
| StructuredClassifier-ownedAttribute, Property-class | Port ownership/inverse transfer and stable identity | Move, rejected containment cycle with exact export rollback, detach and reattach |
| ConnectorEnd-definingEnd, Port-provided/required, ConnectableElement-end | End index determines associated end; conjugation swaps interfaces | Reverse ends, conjugate, XMI save/load with object identity checks, delete an end |

The 2.4.1 `Property-isCompatibleWith` OCL tests `p` against the metaclass of
`self`; 2.5.1 tests `self` against the metaclass of `p`. The 2.4.1 prose conflicts
with its OCL. This matrix preserves the existing declared-version policy, rather
than silently applying a guessed correction. The 2.4.1 opposite excludes
association-owned ends; 2.5.1 does not. The documented interpretation correcting
the repeated lower-bound clause in `Property-isConsistentWith` is retained.

Run: `python -m unittest discover -s tests -p test_classifier_conformance_matrix.py -v`.
Expected booleans and object sets are authored in the tests; neither native
predicates nor their registration tables generate the expected results.

## Independent structural interchange

Run in a separate virtual environment:

```sh
python -m pip install -r requirements-interoperability.txt
python -m scripts.verify_independent_xmi
```

The independent implementation is [PyUML2](https://github.com/pyecore/pyuml2),
pinned to commit `bbea7442b2f4ba0870c42c15e4738e86ba90ea49`, with PyEcore 0.15.2.
These are test dependencies only. PyUML2 is not an exact 2.4.1/2.5.1 semantic
oracle; this test checks the shared structural subset with an authored graph.

For each version, UmlLib builds and exports a 16-element model containing
inheritance, a bounded composite property, ports, an association and a typed
connector. PyUML2 imports it, serializes it, and UmlLib imports that serialization.
Both the independent import and the returned graph are compared to the same
authored expected metaclasses, values, containment and references. Every reference
must point to the actual contained object, not a duplicate or unresolved proxy.
The test oracle also has deliberate corruption controls for multiplicity, type,
end order and ownership in `tests/test_interchange_oracle.py`.

Direct PyUML2 import of the OMG export is **unsupported** in the tested revision.
The test-only adapter performs four explicit dialect operations:

1. Map UML and XMI namespace declarations to the implementation dialect.
2. Remove the UmlLib version-metadata extension.
3. Encode local `xmi:idref` children as reference attributes, keeping IDs/order.
4. Spell the keyword feature `class` as PyUML2's `class_`.

No UML types, values or reference targets are migrated. Return import selects
the original semantic version explicitly because the Eclipse namespace does not
identify it. This is **adapted interchange**, not native OMG-dialect support in
PyUML2 or semantic migration between versions. Profiles, external resources,
unlimited literal serialization and the whole UML metamodel are outside this
independent fixture. Complex models remain covered by the separate public corpus.

The `independent-xmi` CI job runs the pinned external implementation and uploads
source/adapted/returned files and `report.json`; a failed check fails the job.
Local verification passed for both versions on Python 3.14.

## Remaining priority

Extend these independent boundary oracles to operation signatures, additional
subsetting contexts and connector part/port constraints, then to the other UML packages.
Obtain native interchange evidence from another complete UML tool and enlarge
the external fixture to multi-resource models and profiles. The bounded grids
and fixed edit sequences here do not exhaust arbitrary graph mutations or the
normative prose requirements listed in `CONFORMANCE_BACKLOG.md`.
