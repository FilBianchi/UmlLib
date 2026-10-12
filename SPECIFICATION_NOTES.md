# Interpretation notes for the vendored UML 2.5.1 XMI

Python translations preserve the source formula's intent. When the XMI's formula
conflicts with its prose or references a nonexistent metaclass, the choice is
recorded here. These choices are project interpretations, not published OMG errata.

The specification's conformance chapter gives machine-readable artifacts precedence
when they conflict with the PDF. A project interpretation that changes an XMI body
therefore remains a divergence to resolve, not an assertion of normative equivalence.
The expanded report preserves source descriptions and bodies so these choices can be
reviewed independently; a complete decomposition of additional PDF prose is pending.

## CommonStructure and Values audit (0.3.0)

- `NamedElement.qualifiedName`, `ElementImport.getName` and `LiteralString.stringValue`
  declare mandatory returns, although their bodies can return an absent optional name
  or string value. Result contracts use an optional lower bound only for these queries.
- `Namespace.getNamesOfMember` constructs a set containing element.name. An unnamed
  member therefore produces a null entry; the result contract preserves that entry
  only for this query. Other collections reject null elements.
- `NamedElement.allOwningPackages` returns null when the namespace is not a Package,
  despite its collection signature. Python represents that branch as an empty list.
  It does not search through non-Package namespaces to find outer Packages.
- `OpaqueExpression.result` uses behavior.ownedParameter->first() in XMI. The property
  description calls it the return parameter. Python keeps the explicit source body;
  selecting the first input parameter is a documented inconsistency, not a resolved
  implementation of the prose requirement.
- `OpaqueExpression.isIntegral` is explicitly false in the generic source body.
  Its sign/value queries require isIntegral; calls fail that precondition by default.
  This library does not infer executable behavior from an arbitrary language string.
- `DurationConstraint.firstEvent` and `DurationObservation.firstEvent` have no
  isOrdered/isUnique overrides in XMI: they default to an unordered unique collection
  of Booleans. Repeated flags are deduplicated. The pair-of-event interpretation needs
  a normative source resolution before it can be considered fully implemented.
- `Constraint.boolean_value` accepts a computable specification only if its Boolean
  query is defined (false is valid). A LiteralString annotated with a Boolean type
  is rejected. Foreign expressions use declared static Boolean type evidence;
  that evidence does not prove runtime execution or absence of side effects.
- Multiplicity bound queries explicitly default to 1 when the bound query is undefined.
  Invalid literal kinds are reported by lower_is_integer/upper_is_unlimitedNatural;
  replacing that fallback would diverge from the current XMI bodies.

## Earlier project interpretations

- `Namespace-excludeCollisions`: the formula compares each imported element to
  itself and therefore rejects all of them. The prose describes collisions between
  different elements. Python excludes self comparisons. Alias and collision tests
  cover successful imports and two distinct elements with the same name.
- `Package-makesVisible`: the formula compares importedElement to a VisibilityKind
  and uses notEmpty on a collection of Booleans. Python follows the prose about public
  or unspecified visibility, and checks public import/reexport visibility separately.
  Private members and private reexports have explicit tests.
- `Property-isCompatibleWith`: TypeElement is not a UML metaclass in this XMI.
  The implementation uses TypedElement, which is referenced by the same formula's cast.
- `Property-isConsistentWith`: the upper-bound clause repeats the lower-bound test.
  Python checks that the redefining property's upper bound does not exceed the original,
  alongside its lower bound and type conformance. Tests cover narrowing and widening.
- `StateMachine-ancestor`: the formula's top-level-state branch conflicts with the
  documented direction of ancestry. Python checks whether s2 is an ancestor of s1,
  including equality, using the actual containment chain. Tests cover both directions.
- `StateMachine-LCA` / `StateMachine-LCAState`: Python traverses containment chains
  explicitly, handling missing common ancestors with None instead of uncontrolled
  recursion through null vertices. Tests cover siblings in orthogonal regions.
- `Pseudostate-transitions_outgoing` / `Pseudostate-transitions_incoming`: "any pair"
  is interpreted as two distinct transitions, avoiding self-pairs that cannot occupy
  two different regions. Duplicate endpoints still fail the orthogonality condition.
- `Region-belongsToPSM`: Python requires a valid containing machine; a dangling region
  produces an invalid query instead of the vacuous true in the source implication.
- `Behavior-behavioredClassifier`: its source body is labeled as a precondition.
  Python implements the described upward search and returns None when no classifier exists.

No Python evaluation path treats an untranslated definition as satisfied.

- `Transition-isConsistentWith`: its source refers to `source.redefinedTransition`,
  which does not exist on Vertex. Python checks `redefinedVertex` on the redefining source.
- `Vertex-isConsistentWith`: the formula uses an undefined `redefinedElement`
  parameter and reverses the described owner relationship. Python checks whether
  the redefining vertex owner redefines the original vertex owner.
- `Gate-isInsideCF` / `Gate-isOutsideCF`: the implication gives a vacuous true
  for a gate that has no CombinedFragment or opposite end. Python follows the prose
  and returns false outside that domain. Association-owned ends are navigated inversely.
- `Gate-matches`: explicit parentheses preserve the conjunctions described in the
  prose, including name/signature equality and the two directional implications.
- `Message-messageKind`: the body recursively refers to the derived property itself.
  Python derives complete/lost/found/unknown from the presence of send and receive ends.
- `Message-signature_is_signal`: Python compares all signal attributes, including
  owned attributes; the source uses inheritedMember alone and excludes owned members.
- `ConditionalNode-clause_no_predecessor`: Python permits ordinary predecessors
  in the same ConditionalNode and rejects predecessor cycles.
- `ParameterSet-two_parameter_sets`: self pairs are excluded and parameter-set
  cardinalities are compared; the source compares singleton object collections.
- `DecisionNode-parameters`: the prose requires one return parameter; the source
  counts parameters whose direction is not return. Python follows the prose.
- `DecisionNode-decision_input_flow_incoming`: an absent optional decisionInputFlow
  does not require incoming to contain null.
- `ActivityPartition-represents_property`: the ownership check uses the represented
  Property's owner, following the prose.
- `ObjectNode-input_output_parameter`: the final type check is applied to the output
  parameters instead of repeating the input-parameter check.
- `Actor-associations`: the associated endpoint is checked via its type rather than
  Property::class, which identifies an attribute owner.
- `Pin-upperBound`: ObjectNode's property and MultiplicityElement's query have the
  same name. The property has normal attribute access; `uml_operation` selects the query.
- `Behavior-context`: a temporarily unowned behavior has no context classifier.
  Ownership validation still reports the missing owner.
- `InformationFlow-sources_and_targets_kind`: kind tests apply to each endpoint,
  rather than to the InformationFlow itself as the source's unqualified tests imply.
- `InformationFlow-must_conform` (20.2.1.5): classifier ends use nominal UML
  conformance; a typed part can conform to a classifier end. Different parts with
  the same type remain distinct references. Directed Relationship realizations may
  be reversed as stated in the prose. Undirected associations/connectors partition
  distinct ends between source and target groups; directional activity edges and
  messages preserve their direction. This is an explicit project interpretation of
  the prose-only constraint, with valid/invalid tests rather than an OMG certification.
- `InformationItem-has_no` / `not_instantiable` (20.2.2.5): Python follows the prose
  as well as the formula, checking associations and actual InstanceSpecifications
  in the current extent, not only feature/generalization flags and isAbstract.
- `PartDecomposition-assume` / `commutativity_of_decomposition` (17.12.24.4):
  projection recursively matches operands, preserves positions of occurrences relative
  to global constructs, and checks nested InteractionUses. Partial internal constructs
  are not required counterparts. Extra-global status and non-message gate mappings
  are explicit facts because core UML does not encode them as properties. The
  correspondence does not use graphical coordinates or assume status from coverage.
- `Profile-references_same_metamodel` (12.4.7.5): the OCL formula only checks a
  nonempty union. Python enforces the prose's shared base metamodel using identity
  of the outermost owning Package, rejecting unowned references or different roots.
- `Stereotype-name_not_clash`: matching is case-insensitive, consistent with the
  stereotype-name matching convention in 12.3.4. Standard keywords currently derive
  from extended metaclass names, not every optional vendor-specific diagram keyword.
- Runtime stereotype applications implement the mutually exclusive base links of
  12.3.3.4 and the required/duplicate application rules of 12.3.3.6. Required
  applications are created by `apply_profile`; incremental manual profile construction
  reports omissions during validation. Direct edits to profileApplication collections
  do not run the removal API's lifecycle cleanup; `unapply_profile` performs cleanup.
- Prose-only runtime/layout rules are checked to the extent represented by core UML.
  Missing language facts or occurrence mappings remain explicit unsupported obligations.
- `Classifier-directlyUsedInterfaces`: the formula traverses supplierDependency and
  returns clients. Python follows the Usage definition (the client requires the supplier)
  and traverses Usage dependencies whose client is the classifier, returning Interface
  suppliers. See the Usage semantics and required-interface descriptions in the
  [OMG specification](https://www.omg.org/spec/UML/2.5.1/PDF).
