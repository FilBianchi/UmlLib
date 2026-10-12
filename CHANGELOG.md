# Changelog

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
