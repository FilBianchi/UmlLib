# Changelog

## 0.4.0

`UmlElement.delete()` performs logical deletion with composite cascade, cleanup of
incoming/outgoing references and inverse associations, extent removal and stereotype
application cleanup. Restrict/no-cascade policies refuse unsafe deletions without
mutating the graph; failures roll back model edits and runtime application links.
Tombstones cannot be read, edited, queried, validated or reused as UML references.
Official semantic mappings and analyzer facts are invalidated when their targets
are deleted. Required references left absent remain explicit validation failures.

ModelSession now strongly retains live elements until deletion, independent of GC;
the shared default extent remains weak for backward compatibility. Cross-session
incoming references are cleaned without deleting unrelated elements.
Profile unapplication now deletes removed modeled applications/slots, and failed
profile application removes its temporary ProfileApplication from the logical extent.

Classification and SimpleClassifiers have linked boundary examples for all 49
invariants, 41 declared queries, 17 derivations and 6 preconditions. The audit fixes
two classifier-template constraints that incorrectly combined formal and actual
checks, inverse synchronization that confused inherited association ends, and the
UnlimitedNatural default's string representation. Nonfinite Real assignments are
rejected. Four additional nullable query/source signature conflicts are documented.

187 tests pass. The matrix has 244 records with linked examples. Source divergences
in Property and ParameterSet remain visible; this release does not declare complete
UML conformance or implement execution of arbitrary model expressions.

## 0.3.0

Native operation results now enforce declared types, multiplicity, ordering and
uniqueness. Invalid results raise `umltools.OperationResultError`; arguments also
enforce collection contracts before dispatch. Four nullable XMI signature/body
inconsistencies have narrow, documented interpretations.

Stored subsets now synchronize properties that redefine their declared supersets.
This repairs classifier template parameters whose owned formal classifier previously
had no effective templateParameter link. Constraint.boolean_value checks the actual
Boolean query for computable values instead of accepting a misleading type annotation.

The requirements report includes 549 stored properties, 328 association-owned
properties, 23 preconditions, 13 enumerations, signatures, descriptions and review
states in addition to operations, invariants and derivations. Additional normative
PDF prose remains to be decomposed; the inventory is not a full conformance proof.

150 tests pass. All 38 CommonStructure/Values invariants and their declared queries
and derivations have linked examples, including invalid and boundary cases. The
report has 136 records with behavioral examples, including links to earlier tests.
Opaque execution, contradictory source definitions and future audit work remain
explicit limitations. See SEMANTIC_COVERAGE.md and PLAN_CONFORMANCE.md.

## 0.2.0

InformationFlow validation now checks classifier conformance, typed association ends,
n-ary/reflexive channels, exact part identities and directional messages/edges.
InformationItems reject associations and modeled instances. Previously some valid
subtype channels failed, while some invalid endpoint combinations were accepted.

PartDecomposition now projects nested operands and verifies occurrence order, unique
formal-gate matches and nested InteractionUse commutativity. Boundary facts absent
from core UML have explicit mapping APIs and remain unsupported until supplied.

Runtime stereotype applications enforce one base binding, metaclass compatibility,
profile availability, required extensions and duplicate restrictions. Profile application
creates required instances transactionally; removal cleans up inaccessible applications.
Generic InstanceSpecification/Slot applications receive the same base-link checks.
Profiles now reject references to different base metamodel roots.

117 tests pass locally. The semantic report separates native registration from
explicit behavioral-example links for 18 audited specification rules. This release
does not claim complete UML conformance; remaining boundaries are documented in
SEMANTIC_COVERAGE.md.

## 0.1.0

Initial independently installable core UML metamodel, native semantic dispatch,
packaged XMI, CI and GitHub Releases distribution.
