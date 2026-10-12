# Changelog

## 0.12.0

Runtime stereotype applications now expose typed tagged values with inherited/redefined
properties, literal defaults, multiplicities, readonly construction values, enumerations
and UML metaclass references. ProfileObject represents profile-defined Class/DataType
instances distinctly from UML InstanceSpecification; DataType values are immutable.
Binary navigable association ends synchronize atomically, with bounded inverses and
composite ownership/cycle checks. Deletion and profile removal clean runtime references
and composite descendants while preserving values accessible through other profiles.

Strict profiles provide metaclass/element availability views and checked creation,
including reference precedence, imports, extended subtypes and conflict rollback.
User constraints accept trusted Boolean Python callbacks or computable Boolean literals.
Callback mutation through public APIs is rejected; arbitrary OCL is not executed.
313 tests pass. Custom value/derived/default evaluators, non-navigable runtime navigation,
distinct repeated-link identities, non-UML adapters, CMOF and serialization remain open.
Existing metaclass predicates and full-conformance limitations remain separately reported.

## 0.11.0

The structural audit inventories 950 property/end declarations (549 stored, 73 derived,
328 association-owned). Every stored declaration has default/wrong-type and declared-type
setter sweeps. Relationship family scenarios and per-definition evidence are scoped
separately; metadata type/reference/bounds checks report no unresolved declarations.
CI/release verify structural-audit.json and STRUCTURAL_AUDIT.md reproducibility.

Unique collections deduplicate before enforcing upper bounds. StructuredActivityNode
inverse assignment establishes the direct opposite before inherited composite ends.
Stored redefinitions use replacement rather than subset union, and differently named
ancestor setters route through the effective redefined end. Rebinding/clear operations
preserve alias values, ownership, cached collections and transactional rollback.
Cached collection repr/equality reject logically deleted owners.

Cross-session references remain supported but validate reports cross session reference
for stored links, exposing the incomplete local allInstances view. Scalar inverse
rebinding can transfer ownership atomically; adding directly to another composite
collection still requires detachment. 291 tests pass. Per-end semantic proof and
arbitrary mutation/prose coverage remain open, distinct from declaration sweeps.

## 0.10.0

Five supplemental static prose requirements are integrated into validate(), preserving
the 449 declared XMI predicates. They check selection/transformation variance along
control-node paths (including intervening transformations), ordered decision token
inputs, direct reply argument types and configured Artifact-instance manifestations.
Unknown token evidence is unsupported; failures use stable prose: identifiers.

The additive deployed_elements resolver unions direct manifestations of Artifact
objects and Artifact classifiers of modeled instances. Invalid deployed instances
cannot make configured-instance validation pass vacuously. Source deployedElement
behavior is preserved; nested/inherited artifacts, slots and runtime copies remain open.

An operational census of known limitations is generated into CONFORMANCE_BACKLOG.md
and conformance-backlog.json, with priority, source, next action and implemented
supplemental links. CI and release builds check its reproducibility.
280 tests pass; 763 definition records have examples, including five supplemental
requirements and one resolver. Behavior purity and broader normative/structural
requirements remain explicit work rather than inferred from static type checks.

## 0.9.0

UseCases, Deployments and InformationFlows have examples for 18 invariants, two
queries and one derivation. 273 tests pass; 757 definition records have examples.
All 14 packages now have a first audit of the 449 declared invariants, 205 operation
declarations, 73 derivations and 23 preconditions. This is not full UML certification.

Node.internal_structure checks each part's type rather than testing Property as Node.
UseCase subject checks reject shared subjects even when both cases have additional
distinct subjects. Source/prose divergences are preserved in the report.

New cases cover include diamonds/cycles, extension-point ownership, association
endpoint types, overlapping subjects, communication paths, deployment configuration,
manifestation deduplication, represented information-item target subsets and cleanup
after deleting artifacts, instances, associations and mapped gate endpoints.
The Artifact-only deployment derivation and its vacuous instance-deployment checks
remain explicitly partial; endpoint mappings and unsupported external channels stay explicit.

## 0.8.0

Interactions has linked examples for all 49 declared invariants, 14 queries,
one derived property and three precondition records. Existing part-decomposition
projection/mapping cases remain included. 262 tests pass; 742 records have examples.

Nested fragments are visited before following siblings when checking occurrence order.
Guard context traversal now handles InteractionOperand ownership. Outside gate name
uniqueness excludes matching inside gates. Gate.getOperand permits the body's explicit
null branch despite the source's mandatory return signature. Interaction loop bounds
report unknown numeric expressions as unsupported and wrong literal kinds as invalid.

Source differences and preserved reply-argument loopholes are documented. Structural
order checks do not prove full parallel/alternative trace semantics; general global/
write-once state, expression execution and graphical guard placement remain partial.

## 0.7.0

Activities and Actions have linked examples for all 205 declared invariants,
31 query declarations (29 concrete and two abstract), and 9 derived properties.
250 tests pass; 678 definition records now have explicitly linked examples.

StructuralFeatureAction handles a scalar featuringClassifier correctly. ActionInputPin
checks outgoing edges of its producer instead of the receiving pin. ObjectNode
selection outputs conform toward the node type, allowing subtype outputs.
ObjectFlow bound/constant-weight checks distinguish represented numbers, invalid
literal kinds and unknown numeric/constancy evidence; unknowns no longer pass silently.

Scenarios cover call direction/variance/bounds, signal acceptance/reply, variable
scope, association-end bags/qualifiers/indices/visibility, structured boundaries,
conditional clauses, loop variables, exception handlers and graph cycles.
Source/prose conflicts and partial selection/transformation/decision prose checks
are explicit in the matrix. This release audits static models, not token execution
or arbitrary Behavior purity. Existing conformance obligations remain open.

## 0.6.0

CommonBehavior and StateMachines have linked examples for all 54 declared invariants,
35 queries, 11 derivations and 8 precondition records. One finder-body reference is
a malformed Boolean precondition in the XMI and remains a documented source conflict.

Unspecified Behavior methods no longer fail the context-feature check. Protocol
history, state behaviors and transition kinds are checked through nested owned regions.
Composite-state entry/exit points resolve their containing machine. Nested region
redefinition uses State.redefinedVertex instead of the nonexistent redefinedState.
LCAState now respects exact State tests, excludes FinalState endpoints as declared,
and permits the body's explicit null branch despite its conflicting return signature.

TimeEvent validation checks represented computable TimeExpression.expr values;
uninterpreted expressions and observations remain unsupported obligations. No clock,
scheduler or state-machine execution engine is supplied. Source/prose differences,
including stronger recursive protocol checks, are explicit project interpretations.

224 tests pass; 433 definition records have linked examples. The matrix detects eight
duplicated State/Vertex XMI identifiers and preserves operation-local bodies and
conditions instead of silently looking up the other declaration. ProtocolConformance
behavioral proof remains partial; static link modeling is supported.

## 0.5.0

Packages and StructuredClassifiers now have linked examples for all 36 declared
invariants, 29 queries, 20 derivations and the Package.makesVisible precondition.
The audit covers import/reexport visibility, nested profiles, extensions, association
arity and ordered specialization, AssociationClass ownership, component realizers,
conjugated ports, connector bounds and collaboration role correspondence.

CollaborationUse.client_elements now navigates the structuredClassifier/collaboration
association ends instead of using Element.owner. This accepts externally declared
formal roles and rejects mismatched association context sets. Connector correspondence
uses the represented owning classifier for inherited roles; unowned uses with multiple
possible binding contexts remain unsupported instead of selecting an arbitrary one.
This context selection is an explicit interpretation of the XMI's any(true) expression.

206 tests pass; 325 definition records have linked examples. The report includes the
new package audits and flags source conflicts separately from partial prose semantics:
PackageMerge reconciliation, ProfileApplication.isStrict enforcement and the complete
tagged-value/constraint API remain incomplete. This is not full UML certification.

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
