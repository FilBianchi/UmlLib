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

## Classification and SimpleClassifiers audit (0.4.0)

- `Property.opposite`, `Operation.lower`, `Operation.upper` and `Operation.type`
  can return null according to their bodies and optional derived properties, despite
  mandatory query result signatures. Contracts use optional results only for these
  named queries, as for the earlier nullable source conflicts.
- The two ClassifierTemplateParameter conformance constraints quantify different
  objects: one checks substitution actuals, the other checks parameteredElement.
  Their Python implementations are now separate; an invalid formal does not change
  the result of the actual-only rule and vice versa.
- `Property.binding_to_attribute` casts ts.formal to Property, but formal is a
  TemplateParameter. Python follows the attribute-binding description by inspecting
  formal.parameteredElement. This remains a project interpretation of the source.
- `ParameterSet.two_parameter_sets` includes self pairs and compares size on the set
  object rather than its parameters. Python checks distinct ParameterSets for equal
  parameter memberships. The project correction remains flagged as a source conflict.
- `Classifier.allSlottableFeatures` includes inherited attributes through allParents,
  in addition to StructuralFeature members; this can include private parent attributes.
  The audit preserves that explicit XMI body rather than silently filtering visibility.
- Existing corrections for Property.isCompatibleWith (TypeElement/TypedElement),
  Property.isConsistentWith (upper-bound clause), and Classifier.directlyUsedInterfaces
  are now also flagged in the review matrix.
- SimpleClassifiers invariants are tested as declared. General execution of methods,
  signal delivery and primitive domain definitions is not supplied by this audit.

Logical deletion is a Python lifecycle API, not a fabricated metamodel operation.
Cleanup detaches references and leaves ordinary referrers alive; it does not infer
semantic repairs or cascading deletion of every dependent relationship. Persistent
ModelSession extents retain live elements; the default shared extent stays weak.

## Packages and StructuredClassifiers audit (0.5.0)

- `CollaborationUse.client_elements` compares sets at association-owned opposite ends:
  ConnectableElement::structuredClassifier and ::collaboration. Python now navigates
  the associations via declared role membership. A role's Element.owner is a different
  concept; suppliers may be declared outside their Collaboration. Empty opposite sets
  compare equal as in the OCL body; separate ownership/role constraints still apply.
- `CollaborationUse.connectors` chooses a context with any(true) in the source, which
  can select a declaration owner even when an inherited role is bound in a subclass.
  Python prefers the represented CollaborationUse owner when allRoles contains the
  bound roles. Otherwise it requires one shared association context; ambiguous unowned
  uses remain unsupported. This is a documented source interpretation, not OMG errata.
- `ConnectorEnd.multiplicity` unconditionally invokes compatibleWith(definingEnd),
  although definingEnd is null for untyped Connectors. Python follows the prose's
  conditional "if any": there is no association-end restriction in that case.
- `Port.encapsulated_owner` compares owner to encapsulatedClassifier, so two absent
  ends compare equal. Python requires an actual EncapsulatedClassifier owner according
  to the ownership description; unowned ports remain incomplete models.
- `Package.containingProfile` recursively navigates namespace with no root guard in
  its body. Python returns null at an unowned non-Profile Package, consistent with
  the optional result signature. An unowned Stereotype has no valid containing profile.
- The makesVisible formula's enum comparison/Boolean-collection conflict remains
  a project correction, with explicit private-import and alias-reexport examples.
- PackageMerge reconciliation and ProfileApplication.isStrict restrictions are prose
  semantics beyond the represented links/Boolean. They are flagged partial, together
  with the complete stereotype tagged-value and user constraint API; this audit does
  not claim those requirements are implemented.

## CommonBehavior and StateMachines audit (0.6.0)

- Behavior.specification is optional. The unguarded feature_of_context_classifier
  formula rejects unspecified behaviors. Python checks feature membership only when
  a specification is represented; this is a project interpretation of the missing guard.
- Behavior.behavioredClassifier references its finder body as a precondition. This
  returns a classifier/null, not Boolean. The finder and argument contracts are
  implemented; the malformed precondition is not claimed as a valid predicate.
- FunctionBehavior parameter types use exact isTypeOf(DataType), while nested attribute
  types use isKindOf(DataType). Python preserves the distinction even for PrimitiveType
  parameters; the broader DataType prose remains a source conflict.
- ProtocolStateMachine formulas inspect only top-level regions. Python follows the
  machine-wide descriptions for history vertices, entry/exit/do behaviors and protocol
  transition kinds through nested owned regions. Referenced submachines are separate.
- Vertex.containingStateMachine omits entry/exit points owned by a composite State.
  Python follows that State's represented containing machine when stateMachine is absent.
- Region.isRedefinitionContextValid refers to State.redefinedState, which does not exist
  in the supplied metamodel. Python uses redefinedVertex and requires a State target.
- LCAState uses exact State tests; FinalState endpoints are excluded. Its mandatory
  signature conflicts with an explicit null branch. The effective result is optional.
- Vertex.isConsistentWith has State-prefixed identifiers duplicated by State's actual
  declaration and uses an undeclared redefinedElement. Python follows the argument and
  owner redefinition relation. The matrix preserves both local operation bodies and
  reports eight ambiguous XMI IDs instead of overwriting one declaration with the other.
- TimeExpression does not override integerValue, so the TimeEvent formula cannot read
  even a represented integer expr directly. Python checks computable expr evidence;
  observations and foreign expressions stay unsupported without numeric evaluation.
  This does not execute languages, clocks or scheduling behavior.
- Existing ancestor, region-containment and distinct fork/join-pair interpretations
  are flagged in the review matrix. An unowned Region is not assumed protocol-owned
  merely because the source implication is vacuously true.
- ProtocolConformance links are structural data. Behavioral conformance proof and
  general state-machine execution are not supplied by this static audit.

## Earlier project interpretations (continued)

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
