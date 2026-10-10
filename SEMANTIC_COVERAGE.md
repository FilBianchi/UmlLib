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
  non-message occurrence whose actual-gate mapping is absent remains an unsupported
  obligation. The core metamodel has no explicit mapping for this case.
- Guard placement is checked at the core model level (ownership by its operand).
  Pixel coordinates and layout belong to UMLDI and are outside this distribution.
- The runtime condition that only one stereotype base slot is populated requires
  stereotype application instances; metamodel base-property multiplicities are checked.

Models with unsupported or invalid obligations must not be described as fully validated.
Unknown expression languages are never implicitly accepted or executed.

## Behavioral verification

68 tests cover class/package inventories and inheritance; atomic collection edits,
reversal, ownership and cycles; stored subsets and inverse associations;
names, alias imports and reexports; classifier inheritance and property redefinition;
multiplicities and unlimited values; state and protocol machines; call signatures;
variable scope and nested actions; use-case inclusion cycles; component interfaces,
conjugated ports and ordered connector ends; message kinds and gates; expressions,
deployment manifestations, profiles and object flows through control nodes.

Tests distinguish valid and invalid models and make the OCL evaluator fail if called.
CI runs Python 3.10, 3.12 and 3.14, checks reproducible generation and the inventory,
builds distributions and imports an installed wheel from outside the checkout.

## Scope and future conformance work

This package covers the core UML 2.5.1 metamodel XMI, not StandardProfile or UMLDI.
Those are separate specifications and would need their own modules and tests.
Further conformance work should broaden independent examples for every individual
rule, formalize language-adapter and decomposition mappings, and compare behavior
against additional UML implementations. An inventory of translated functions alone
cannot replace that evidence.
