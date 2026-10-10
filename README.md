# UmlLib

Install a versioned wheel directly from GitHub Releases:

```console
python -m pip install https://github.com/FilBianchi/UmlLib/releases/download/v0.1.0/umllib-0.1.0-py3-none-any.whl
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

`validate()` returns `(category, specification_id)` issues: `multiplicity`,
`constraint`, `invalid constraint`, `unsupported constraint`, `invalid derivation`,
and `unsupported`. Successful rules are omitted. `float('inf')` represents UML's
unlimited natural value `*`.

Use separate extents when working on independent models:

```python
from umltools import ModelSession

with ModelSession() as session:
    model = Uml.Packages.Model(name="Independent")
```

Queries on these objects continue to use that session after leaving the context.
The default extent is shared for compatibility. Stored subset properties synchronize
their supersets transactionally, and derived unions remove duplicate elements.

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

See [SEMANTIC_COVERAGE.md](SEMANTIC_COVERAGE.md) for remaining requirements.
[semantic-report.json](semantic-report.json) inventories Python translations and
outstanding definitions. Registration counts are not conformance guarantees.
[SPECIFICATION_NOTES.md](SPECIFICATION_NOTES.md) records interpretations of ambiguous XMI.

UmlLib was extracted from [UmlTools](https://github.com/FilBianchi/UmlTools);
this repository distributes the Python library independently of its Qt viewer.
