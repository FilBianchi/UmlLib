# Native Python semantics coverage

The UML runtime uses explicit Python translations; it never executes OCL text.
This initial release does not claim certified UML 2.5.1 conformance.

## Inventory

`python semantic_report.py` regenerates identifiers and implementation locations.

| Definition | Native Python | Structural union | Abstract declaration | Untranslated |
| --- | ---: | ---: | ---: | ---: |
| Operations | 203 | 0 | 2 | 0 |
| Class invariants | 449 | 0 | 0 | 0 |
| Derived properties | 55 | 18 | 0 | 0 |

The 242 metaclasses and 13 enumerations are organized into 14 specification packages.
Inherited definitions are counted once, at the declaring metaclass. Operation
preconditions are implemented in the query functions. Abstract CallAction operations
require a concrete override; they do not contain a fabricated body.

The expanded matrix also records 549 stored class properties, 328 association-owned
properties, 23 preconditions, 13 enumerations and 242 class descriptions. Signatures,
property bounds/defaults/subsets/redefinitions, source bodies and comments are
preserved. Review status is separate from registration and example linkage.
No postconditions are declared in this core XMI. Additional normative PDF prose
still needs decomposition into individual requirements; phase 1 is not closed.

Registration coverage is not a correctness score. Predicates translated from prose
and corrections to inconsistent formulas are project interpretations documented in
SPECIFICATION_NOTES.md. In particular, runtime behavior and diagram placement cannot
always be established from a static core UML model.

## Validation obligations that need application information

- Opaque language expressions need analyser facts about references, constancy and
  absence of side effects. `register_expression_facts` supplies trusted facts;
  literals and StringExpressions are handled directly. Missing facts produce
  `unsupported constraint`, and negative facts produce a constraint failure.
- A single-token domain collection type needs `register_collection_type`. A
  multivalued pin directly represents a token collection.
- Part decomposition handles structural correspondence and message gates. A
  non-message occurrence needs `map_occurrence_gate`; a fragment's extra-global
  status needs `mark_extra_global`. A gate-order anchor must be represented or
  explicitly mapped. Missing information remains an unsupported obligation.
- InformationFlow gate endpoints need `bind_gate_endpoint`. Lost/found messages
  whose external end is not modeled remain unsupported as complete channels.
- Guard placement is checked at the core model level (ownership by its operand).
  Pixel coordinates and layout belong to UMLDI and are outside this distribution.
- Stereotype base-binding exclusivity, duplicates, abstract instances, required
  extensions and profile availability are checked by `umltools.stereotypes`, and
  for applications modeled with InstanceSpecification/Slot. User-defined tagged-value
  classes, arbitrary executable stereotype constraints and XMI serialization of
  runtime applications are not implemented by this API.

Models with unsupported or invalid obligations must not be described as fully validated.
Unknown expression languages are never implicitly accepted or executed.

## Behavioral verification

206 tests cover class/package inventories and inheritance; atomic collection edits,
reversal, ownership and cycles; stored subsets and inverse associations;
names, alias imports and reexports; classifier inheritance and property redefinition;
multiplicities and unlimited values; state and protocol machines; call signatures;
variable scope and nested actions; use-case inclusion cycles; component interfaces,
conjugated ports and ordered connector ends; message kinds and gates; expressions,
deployment manifestations, profiles and object flows through control nodes.

The new audit adds valid, invalid and boundary examples for InformationFlow,
InformationItem, PartDecomposition, Stereotype and Profile checks, plus runtime
application lifecycle tests. Explicit `@verifies(...)` annotations link examples to
325 definition records in the JSON report, including properties and preconditions.
All 27 CommonStructure invariants and 11 Values invariants, and their declared
queries/derivations, have examples. Classification adds 44 invariants, 40 queries,
16 derivations and 6 preconditions; SimpleClassifiers adds 5 invariants, 1 query and
1 derivation with examples. Packages adds 14 invariants, 14 queries, 7 derivations
and 1 precondition; StructuredClassifiers adds 22 invariants, 15 queries and 13
derivations with examples. Other invariants still need review and links;
older tests cover some of them. Neither a test count nor
these links constitute certification or exhaustive verification of each rule.

Version 0.3.0 checks operation results and argument collections against UML
signatures. A result violating type, bounds, ordering or uniqueness raises
`OperationResultError`. Models may still be temporarily incomplete during
construction; structural validation reports missing required properties. This
increment added result contracts; 0.4.0 adds logical deletion and the next two audits.

The CommonStructure/Values audit includes ownership changes, namespace/name absence,
import collisions, redefined template subsets, multiplicity defaults and infinity,
literal domains, ordered string concatenation and observation cardinalities.
Foreign expression purity and constancy require analyzer facts. OpaqueExpression's
generic integer queries retain the XMI's false body and reject unsatisfied
preconditions; they do not execute Python/OCL text. Source issues are listed in
SPECIFICATION_NOTES.md and flagged in the report.

The Classification audit covers generalization cycles and visibility, redefinition
contexts and variance of parameter multiplicities, template formal/actual separation,
subset contexts and bounds, association navigation, slots, deployment roles,
stream/exception parameters, parameter-set alternatives and inherited signatures.
SimpleClassifiers covers classifier behaviors, immutable enumerations, literal owners,
public interface features and ordered signal/reception signatures. Source conflicts
remain limitations, even when examples verify the documented project interpretation.

The Packages/StructuredClassifiers audit checks public/private imports and alias
reexports, nearest profile containment, extension ends and required flags, stereotype
base multiplicities and metamodel roots; ordered association specialization and
n-ary ends; composite attribute/end exclusivity; direct and inherited parts/roles;
component realization interfaces and conjugated ports; connector kind, types and
multiplicity; and collaboration bindings/corresponding connector types.
AssociationClass's disjoint composite roles are additionally enforced during mutation.

CollaborationUse.client_elements compares opposite association context sets, including
externally declared formal roles, rather than physical ownership. Connector correspondence
prefers a represented owner whose allRoles includes the bound roles (including inherited
ones); absent ownership requires one shared association context. Multiple unowned
contexts remain an unsupported obligation. The choice resolves the source's arbitrary
any(true) traversal by project interpretation; it is not a published normative erratum.

Deletion tests keep ordinary Python references to tombstones, exercise atomic refusal
and rollback (including application cleanup failure), check shared composite subsets,
cross-session cleanup, retained collection handles and required dangling references.
Persistent ModelSession extents retain live objects; the default shared extent remains
weak. Ordinary referring objects survive and may require model repairs. Adapter facts
and official mapping entries that reference tombstones are discarded, not treated as
valid evidence. Arbitrary external application metadata is outside this lifecycle API.

The audit now checks classifier conformance and disjoint channel ends (including
n-ary and reflexive associations), exact part references, message/edge direction,
ordered recursive operand projections, gate uniqueness, nested commutativity,
base-slot exclusivity, transactional profile application and common metamodel roots.

Tests distinguish valid and invalid models and make the OCL evaluator fail if called.
CI runs Python 3.10, 3.12 and 3.14, checks reproducible generation and the inventory,
builds distributions and imports an installed wheel from outside the checkout.

## Scope and future conformance work

This package covers the core UML 2.5.1 metamodel XMI, not StandardProfile or UMLDI.
Those are separate specifications and would need their own modules and tests.
PackageMerge links are represented, but the normative merge/reconciliation algorithm
is not implemented. ProfileApplication.isStrict is stored but its semantic restrictions
are not enforced. A complete typed tagged-value API and arbitrary user-defined stereotype
constraint execution remain missing. The report marks these requirements as partial;
passing the declared XMI invariants does not discharge these prose requirements.
Further conformance work should broaden independent examples for every individual
rule, formalize language-adapter and decomposition mappings, and compare behavior
against additional UML implementations. An inventory of translated functions alone
cannot replace that evidence.
