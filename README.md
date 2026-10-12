# UmlLib

Install a versioned wheel directly from GitHub Releases:

```console
python -m pip install https://github.com/FilBianchi/UmlLib/releases/download/v0.9.0/umllib-0.9.0-py3-none-any.whl
```

The latest downloadable version is listed at
[GitHub Releases](https://github.com/FilBianchi/UmlLib/releases/latest).
Alternatively install from source: `python -m pip install git+https://github.com/FilBianchi/UmlLib.git`.

Pushing a `v` tag matching the version in `pyproject.toml` runs tests, builds the wheel
and source archive, verifies the installed wheel, and publishes them with SHA-256 checksums.
This initial version is alpha; semantic coverage and limitations are documented below.

Python implementation of the UML 2.5.1 metamodel, generated from the vendored OMG XMI.
The library contains 242 metaclasses and 13 enumerations in 14 specification packages.
Python 3.10 or later is required. The library does not require Qt.

```python
import Uml

model = Uml.Packages.Model(name="Shop")
customer = Uml.StructuredClassifiers.Class(name="Customer")
model.packagedElement.append(customer)
customer.ownedAttribute.append(Uml.Classification.Property(name="id"))

assert customer.owner is model
assert customer.qualifiedName == "Shop::Customer"
print(model.allOwnedElements())
print(model.validate(recursive=True))

state = Uml.StateMachines.State(name="Ready")
```

Direct imports also work: `from Uml.StateMachines import State`.
`Uml.StateMachine.State` is an alias for `Uml.StateMachines.State`;
the StateMachine metaclass itself is `Uml.StateMachines.StateMachine`.
The previous `import UML` interface remains available.

Each classifier has its own generated Python source file in its specification package.
Keywords use a trailing underscore (`class_`, `break_`). Runtime metadata and behavior
live in `umltools`; source generation is reproducible:

```console
python generate_uml.py
python -m unittest discover -s tests -v
python semantic_report.py
```

Collections validate edits, maintain navigable opposite associations and composite
ownership, and prevent containment cycles. Detach an element before assigning it
to another composite owner. Lower multiplicities are checked by validation, allowing
incremental model construction.

Operations, derived properties and invariants use explicit Python translations in
`umltools/native`, organized by semantic area and registered against specification
identifiers. The library never falls back to interpreting OCL. An untranslated query
raises `UnsupportedSemanticsError`; untranslated invariants are reported explicitly.
The XMI supplies structural metadata, signatures and reference formulas.

The inventory covers all 203 concrete operations, two abstract operation declarations,
449 class invariants and 73 derived properties. This is implementation coverage, not
a certification of UML conformance. Opaque expressions need facts from their own
language analyser; validation reports missing facts instead of assuming success.

Activities and Actions now have explicitly linked examples for their 205 invariants,
31 query declarations (including two abstract queries) and 9 derived properties.
Interactions has linked examples for 49 invariants, 14 queries, one derivation and
three preconditions. UseCases, Deployments and InformationFlows add 18 audited
invariants, two queries and one derivation. The 0.9.0 suite has 273 tests.
All 14 core packages have a first audit with explicitly linked examples for every
declared invariant, operation, derivation and precondition. These audits check static model semantics: they supply
no token execution engine. Selection/transformation purity and some additional
token-type requirements from the prose remain partial and are listed in
`semantic-report.json` and `SPECIFICATION_NOTES.md`. A successful invariant check
proves only its implemented predicate, not every related prose requirement.
Interaction ordering currently follows represented fragment containment; complete
parallel/alternative trace semantics, graphical guard placement and arbitrary domain
global/write-once storage semantics remain open obligations.
Artifact-instance deployment semantics remains partial: the deployedElement query
preserves the XMI's Artifact-only filter. Additional prose/structural requirements,
source divergences, profiles, XMI model exchange and UMLDI remain separate conformance work.

`validate()` returns `(category, specification_id)` issues: `multiplicity`,
`constraint`, `invalid constraint`, `unsupported constraint`, `invalid derivation`,
and `unsupported`. Runtime stereotype checks additionally report `stereotype application`,
`invalid stereotype application`, or `unsupported stereotype application`.
Successful rules are omitted. `float('inf')` represents UML's
unlimited natural value `*`.

Use separate extents when working on independent models:

```python
from umltools import ModelSession

with ModelSession() as session:
    model = Uml.Packages.Model(name="Independent")
```

Queries on these objects continue to use that session after leaving the context.
The session retains its live elements until explicit deletion or disposal of the
whole session. The default extent remains shared and weak for compatibility;
use ModelSession for a persistent logical extent. Stored subset properties synchronize
their supersets transactionally, and derived unions remove duplicate elements.

Delete model elements independently of Python variable lifetime:

```python
removed = customer.delete()  # Includes composite descendants.
assert customer.is_deleted
```

`delete()` clears incoming and outgoing UML references, cleans inverse links,
removes modeled stereotype applications of the deleted base, detaches runtime
applications and removes deleted elements from extents. Cleanup covers live references
in other sessions. Surviving required references may become absent: validate those
elements to find the resulting incomplete model. Deletion does not repair the meaning
of surviving constraints or automatically delete ordinary referring relationships.

Use `delete(on_references="restrict")` to refuse external UML references, or
`delete(cascade=False)` to refuse composite children. The composite parent link is
allowed in restrict mode. Refused/failed deletion rolls back model edits and
application links. The returned tuple contains removed elements in unspecified order;
repeating deletion returns an empty tuple. Tombstones reject model reads, writes,
queries, validation and reuse with `DeletedElementError`. `is_deleted` remains readable.
Official gate mappings and analyzer facts referencing deleted objects are discarded;
Python variables and arbitrary application metadata remain the application's responsibility.

`Pin.upperBound` is the ObjectNode property; the identically named multiplicity query
is available explicitly as `pin.uml_operation("MultiplicityElement", "upperBound")`.

For an opaque expression, an application can supply analyser facts without executing OCL:

```python
from umltools.expression_semantics import register_expression_facts

register_expression_facts(expression, references=(property_used,), constant=False, pure=True)
```

`register_collection_type(classifier)` declares a domain type whose individual instances
are collections. These declarations are trusted application input. They do not analyse
arbitrary expression strings or prove correctness of executable application behavior.

## Runtime stereotype applications

The Stereotype metaclass describes a classifier; a runtime application links an
instance of that classifier to one model element:

```python
from umltools.stereotypes import apply_profile, apply_stereotype, unapply_profile

apply_profile(model, profile)
application = apply_stereotype(customer, stereotype, base_property="base_Class")
assert application.element is customer
print(application.base_slots)  # Read-only Property -> element/None mapping.
print(application.validate())
```

The profile must define the stereotype and its Extension/base properties. Applying
a profile creates required applications; an ambiguous abstract required stereotype
raises an error and rolls back newly created applications. A stereotype with several
extensions always binds exactly one base property. Rebinding checks the new element
before changing the old link. Applying the same stereotype or its subtypes twice is
rejected. `unapply_profile` removes inaccessible applications while preserving model
elements and applications still available through another applied profile.

Applications modeled explicitly with `InstanceSpecification`, `Slot` and
`InstanceValue` also receive base-binding and duplicate checks. The runtime API covers
base links and profile availability; it does not execute stereotype OCL bodies or
provide a generated Python class for each user-defined stereotype's tagged values.

## Interaction boundary mappings

Core UML omits some facts required by its prose-only constraints. Explicit annotations
allow validation without guessing:

```python
from umltools.interaction_mapping import (
    bind_gate_endpoint, mark_extra_global, map_occurrence_gate,
)

bind_gate_endpoint(message, boundary_gate, participating_part)
mark_extra_global(decomposition, fragment)
map_occurrence_gate(decomposition, occurrence, actual_gate,
                    internal_occurrence=internal_occurrence)
```

Gate bindings identify an InformationFlow participant. Extra-global status describes
a CombinedFragment spanning the decomposition boundary; covering all internal lifelines
alone does not establish that status. Non-message occurrences need an explicit mapping;
message occurrences can infer a unique matching formal gate and its internal anchor.
Mappings are rechecked when models change. They are runtime annotations and are not
currently serialized to XMI.

See [SEMANTIC_COVERAGE.md](SEMANTIC_COVERAGE.md) for remaining requirements.
[semantic-report.json](semantic-report.json) inventories Python translations and
explicit rule/test links. Registration counts are not conformance guarantees; a
definition without linked examples may still have older tests not yet annotated.
[SPECIFICATION_NOTES.md](SPECIFICATION_NOTES.md) records interpretations of ambiguous XMI.

UmlLib was extracted from [UmlTools](https://github.com/FilBianchi/UmlTools);
this repository distributes the Python library independently of its Qt viewer.
