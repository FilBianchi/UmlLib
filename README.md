# UmlLib

Install a versioned wheel directly from GitHub Releases:

```console
python -m pip install https://github.com/FilBianchi/UmlLib/releases/download/v0.15.0/umllib-0.15.0-py3-none-any.whl
```

The latest downloadable version is listed at
[GitHub Releases](https://github.com/FilBianchi/UmlLib/releases/latest).
Alternatively install from source: `python -m pip install git+https://github.com/FilBianchi/UmlLib.git`.

Pushing a `v` tag matching the version in `pyproject.toml` runs tests, builds the wheel
and source archive, verifies the installed wheel, and publishes them with SHA-256 checksums.
This initial version is alpha; semantic coverage and limitations are documented below.

Python implementations of the UML 2.5.1 and 2.4.1 metamodels, generated from vendored OMG XMI.
Each version contains 242 metaclasses and 13 enumerations. `Uml251`/`Uml` provide the
existing 2.5.1 API; `Uml241` provides independent 2.4.1 classes, organized in familiar
convenience groups. The 2.4.1 semantic implementation is still partial; see
[UML_VERSION_BACKENDS.md](UML_VERSION_BACKENDS.md) for precise coverage and isolation.
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
ownership, and prevent containment cycles. Adding to another owner's composite
collection requires explicit detachment. Assigning a navigable scalar inverse can
transfer ownership atomically by removing the previous owner's link first.
Lower multiplicities are checked by validation, allowing
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
invariants, two queries and one derivation. The 0.15.0 suite has 356 tests across both versions.
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

Five supplemental static prose checks now run automatically in `validate()`, with
identifiers prefixed `prose:`: selection/transformation token types, ordered decision
input types, reply argument types and configured Artifact-instance manifestations.
Unknown token types produce `unsupported constraint` rather than a successful check.
The 449 XMI predicates remain independently inspectable through `umltools.native.check`;
a passing XMI predicate may still have a failing supplemental requirement.

```python
from umltools.static_requirements import check_static, deployed_elements

issues = model.validate(recursive=True)  # Includes supplemental requirements.
elements = deployed_elements(Uml.ExecutionEnvironment())
```

`deployed_elements(target)` unions direct manifestations of deployed Artifact objects
and modeled instances' Artifact classifiers. It does not infer nested artifacts,
inherited manifestations, slot overrides or runtime copies. The source-derived
`target.deployedElement` retains the XMI's Artifact-only interpretation.
`CONFORMANCE_BACKLOG.md` and `conformance-backlog.json` list known limitations,
priorities and next actions. Regenerate them with `python conformance_backlog.py`;
CI verifies reproducibility. This census does not replace decomposition of all normative prose.

`STRUCTURAL_AUDIT.md` and `structural-audit.json` inventory 549 stored properties,
73 derived properties and 328 association-owned ends. Every stored declaration has
default/wrong-type and declared-type assignment sweeps; relationship family scenarios
have separately scoped evidence. This does not certify every end's full semantics.
Regenerate with `python structural_audit.py`; CI checks the saved report.

`validate()` returns `(category, specification_id)` issues: `multiplicity`,
`constraint`, `invalid constraint`, `unsupported constraint`, `invalid derivation`,
and `unsupported`. Runtime stereotype checks additionally report `stereotype application`,
`invalid stereotype application`, or `unsupported stereotype application`.
Successful rules are omitted. `float('inf')` represents UML's
unlimited natural value `*`.

`cross session reference` identifies stored references to another ModelSession or
between a session and the default extent. Such references remain allowed and deletion
cleans them; this diagnostic indicates an incomplete local allInstances view, not
an automatic UML semantic violation. Keep a connected model in one session when its
queries require complete reverse/non-navigable association extents.

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
`InstanceValue` also receive base-binding and duplicate checks. Actual profile values
use the runtime API below, distinct from UML instance specifications.

### Typed tagged values and profile objects

```python
import Uml
from umltools import ModelSession
from umltools.stereotypes import apply_profile, apply_stereotype
from umltools.profile_values import ProfileObject, register_profile_constraint

with ModelSession():
    metamodel = Uml.Model(name="UML")
    metaclass = Uml.Class(name="Class"); metamodel.packagedElement.append(metaclass)
    string = Uml.PrimitiveType(name="String")
    stereotype = Uml.Stereotype(name="Documented")
    profile = Uml.Profile(name="Documentation", packagedElement=[string, stereotype],
                          metaclassReference=[Uml.ElementImport(importedElement=metaclass)])
    base = Uml.Property(name="base_Class", type=metaclass)
    stereotype.ownedAttribute.append(base)
    extension = Uml.Extension(memberEnd=[base],
                              ownedEnd=Uml.ExtensionEnd(type=stereotype,
                                  aggregation=Uml.AggregationKind.composite,
                                  lowerValue=Uml.LiteralInteger(value=0)))
    profile.packagedElement.append(extension)
    text = Uml.Property(name="text", type=string,
                        lowerValue=Uml.LiteralInteger(value=0))
    stereotype.ownedAttribute.append(text)
    model = Uml.Model(packagedElement=[Uml.Class(name="Customer")])
    apply_profile(model, profile)
    application = apply_stereotype(model.packagedElement[0], stereotype,
                                   values={"text": "Customer documentation"})
    application.set_value(text, "Updated documentation")
    assert application.get_value("text") == "Updated documentation"
    assert application.tagged_values["text"] == "Updated documentation"
```

Keys are effective Property identities or unambiguous names. Inherited/redefined
properties, Boolean/Integer/Real/String/UnlimitedNatural values, modeled enumeration
literals and referenced UML metaclass instances are supported. `EnumValue` identifies
an enumeration literal. `ProfileObject(classifier, package, values={...})` creates a
profile-defined Class or structured DataType instance; an `InstanceSpecification`
cannot substitute for it. DataType values are immutable after construction.

`set_values` checks the whole update before applying it. Bounds and primitive types
are checked; unique collections deduplicate, ordered collections retain order and
nonunique ordinary tags preserve duplicates. Collection reads return immutable
tuples; `tagged_values` and `values_by_property` are read-only views. Literal defaults
are used when a value is absent. Missing required tags are validation errors; writes
must satisfy lower bounds. Read-only tags can be supplied at construction.

Binary associations synchronize navigable runtime opposite properties atomically.
An occupied scalar opposite rejects a second link; clear it before rebinding.
Composite Class values have one owner, reject cycles and are deleted with their owner.
Removing a profile or deleting a base/schema clears inaccessible runtime values and
references; values still accessible through another applied profile survive.
`application.delete()` also detaches its base. `detach()` preserves its values for
later `rebind()`. Packages retain runtime instances independently of Python variables.

User-defined constraints can register `register_profile_constraint(constraint,
lambda application: ...)`; predicates must return an exact Boolean. Inherited
constraints are evaluated too. False, failed and unavailable evaluators receive
distinct diagnostics. Normal model/value creation, mutation and deletion are blocked
during callbacks. Callbacks are trusted Python code, not a sandbox or a proof of
absence of external side effects. Arbitrary OCL text is never executed.

Custom primitive types use PrimitiveValue as described below; their unknown semantics,
derived tags and nonliteral defaults remain explicit validation obligations.
Association-owned non-navigable runtime
navigation, repeated links requiring distinct link identities and CMOF interoperability
remain open. XMI exchange covers supported runtime values as described below;
these examples do not prove exhaustive profile conformance.

### Strict profile views

`apply_profile(model, profile, is_strict=True)` activates metaclass filtering.
`umltools.profile_filtering.is_metaclass_available(model, "Class")` and
`is_element_available(element)` expose the view; `create_profiled_element(model,
"Class", name="C")` checks it and creates an unowned object in the model's extent.
Ordinary constructors remain available for general editing. Existing hidden objects
are preserved. Explicit metaclass references override metamodel references; imported
profiles and extended metaclass subtypes contribute to availability. Disjoint strict
views are rejected by `apply_profile` and diagnosed by validation after direct edits.
Public imports govern stereotype visibility. Non-UML metaclasses need an adapter.

## XMI import and export

```python
from umltools.xmi import load, loads, dump, dumps

document = load("model.uml")
model = document.roots[0]
print(document.complete, document.diagnostics)
print(model.validate(recursive=True))

model.name = "Updated"
dump(document, "updated.xmi")
restored = loads(dumps(document))
```

The filename extension can be `.uml` or `.xmi`. Imports allocate all UML objects
before linking references, use an isolated ModelSession and retain resource-local
`xmi:id` identities. `document.resolve("id")` retrieves a local object;
`document.resolve("other.uml#id")` resolves a resource-qualified reference.
`resource_roots` contains roots of all loaded files; `roots` contains the entry file's
roots. Forward/cyclic links, containment, scalar/collection values, enumeration values,
UUID metadata and stored subset/redefined ends are supported. Serialized derived and
readonly features are checked against the reconstructed graph rather than overwritten.
Incomplete UML models are allowed; decoding successfully does not mean validate passes.

`load` resolves relative local files beneath the entry file's directory. Network,
`pathmap://` and other external resources require explicit mappings:

```python
from pathlib import Path

document = load("model.uml", resources={
    "pathmap://UML_LIBRARIES/UMLPrimitiveTypes.library.uml":
        Path("libraries/UMLPrimitiveTypes.library.uml"),
})
```

`loads` resolves no local files automatically. Its `resources` values can be XML
bytes/text or Paths; `external_objects` maps absolute `URI#id` references to existing
UML objects. URI aliases mapped to the same physical Path share object identities.
Namespaces are resolved from XML declarations, including QName-valued `xmi:type`
and `xsi:type` and nested prefix rebinding. Common OMG UML and Eclipse UML2 namespace
forms are accepted for features represented by the 2.5.1 metadata; this is not a
general migration guarantee for older metamodels. EMF positional/named URI fragments,
XPointer, CMOF documents and arbitrary non-UML metamodels remain unsupported.

Strict mode is the default: unknown classes/features, missing references, illegal
values and conflicting explicit links raise XmiError (with reference/unsupported
subclasses). A failed import rolls back changes to existing external objects and
removes new UML/runtime instances. `strict=False` permits partial decoding with
resource/ID/feature diagnostics. Unsupported profile values and unknown XML/vendor
extensions are retained as opaque XML when exporting the **document**, not merely
its roots. Opaque vendor semantics, their custom reference encodings and layout are
not interpreted or remapped. Structurally invalid inputs are not automatically repaired.
`complete` indicates no recorded decoding/extension gaps, not UML/XMI certification.

Export bundles the closure of stored references, composite descendants, owners and
supported runtime profile values into one file. IDs remain stable when unique and
are remapped on collisions between source files. Export omits derived caches and
chooses one effective composite containment feature per child. With `bundle=False`,
external targets need imported identities or `external_references={object: "URI#id"}`.
This preserves external links; it is not an automatic rewrite of a multi-file project.

Profile applications use namespaced stereotype elements with base links and typed
tags; inline profile Class composition and separate shared runtime instances are
supported. Explicit empty values preserve the distinction from literal defaults.
An XMI Extension named UmlLib records profile namespace bindings and package contexts
for runtime Class/DataType objects. Other tools may need an adapter for this metadata.
User-defined Python callbacks and analyzer/gate mappings are not serialized. OCL text
is retained as text and never executed. Unknown primitive semantics, derived runtime
tags and arbitrary default evaluators remain explicit validation limitations.

### Values of model-defined primitive types

```python
from umltools.primitive_values import PrimitiveValue

# money_type is the UML PrimitiveType definition read from the model.
value = PrimitiveValue(money_type, "0012.30")
application.set_value("price", value)
application.set_value("price", value.with_lexical("17.50"))
```

PrimitiveValue keeps the exact definition object and immutable lexical text. It does
not infer Python semantics from custom names such as Money, Date, EString or EInt.
XMI automatically creates these values for custom primitive tags; they can be read,
edited, exported and reimported in strict mode. Distinct definitions sharing a name
remain distinct types. Collection bounds/order/uniqueness and readonly/composition
rules still apply. Custom multivalued XML attributes use whitespace-separated lexical
tokens; child elements preserve individual values including whitespace and empty text.
Explicitly typed LiteralString defaults (expression.type is the custom PrimitiveType)
can also provide lexical defaults. Other default expressions require an evaluator.

Unknown primitive semantics are reported during profile/value validation, separately
from successful decoding. `value.to_python()` requires an explicitly registered codec:

```python
from decimal import Decimal
from umltools.primitive_values import register_primitive_codec

register_primitive_codec(money_type, decode=Decimal,
    encode=lambda number: format(number, "f"),
    validate=lambda number: isinstance(number, Decimal) and number >= 0)
value = PrimitiveValue.from_python(money_type, Decimal("12.30"))
assert value.to_python() == Decimal("12.30")
```

Codecs are keyed by type identity, never registered globally by name. Callbacks are
trusted Python code, must obey the Boolean/string result contracts and cannot mutate
the model through public APIs during evaluation. Codecs are not serialized or inferred
from OCL text. Imported definitions need their own registration. Deleting a definition
cleans its values and codec registration. The five existing standard primitive
representations remain built in; custom codecs do not override them.

### UML versions

`document.semantic_version` is currently `2.5.1` for the Python metamodel and its
validation rules. `document.source_dialects` records the actual namespaces per resource,
format and possible UML versions. This distinguishes transport compatibility from
version-specific semantics. `20131001` is intentionally ambiguous between 2.5 and
2.5.1: the normative 2.5.1 metamodel vendored in this repository declares it too.
Eclipse UML2 implementation namespaces are not interpreted as exact UML versions.

`dumps(document, target_version="2.5.1")` is supported. Other target versions raise
an explicit unsupported error; relabeling a namespace would not perform a conversion.
The target versions are 2.4.1 and 2.5.1; 2.5 is not an implementation target.
The normative declaration comparison is recorded in [UML_VERSION_COMPARISON.md](UML_VERSION_COMPARISON.md).
Uml241 now provides a separate structural metamodel, isolated sessions and explicitly
reviewed base semantics; see [UML_VERSION_BACKENDS.md](UML_VERSION_BACKENDS.md).
Full 2.4.1 semantic validation, XMI exchange and migration policies remain open.
2.3 and UML 1.x are not implemented. The public corpus remains a compatibility check, not a multi-version
conformance claim.

The reader rejects DTD/entity declarations and has configurable byte, element and
depth limits. Model queries are memoized only during stable exchange phases; ordinary
mutable model queries keep their existing behavior.

Public integration samples have pinned URLs and SHA-256 hashes in
[scripts/xmi-corpus.json](scripts/xmi-corpus.json). Run the offline cache verification
with `python -m scripts.verify_xmi_corpus`; add `--fetch` to download sources explicitly,
and `--complex` to include Eclipse with its external profiles/libraries. The separate
Public XMI corpus workflow publishes a detailed diagnostic report. Small authored
graph/profile/failure cases run in ordinary CI without network access.
See [XMI_CORPUS.md](XMI_CORPUS.md) for the verified counts and their scope.

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
