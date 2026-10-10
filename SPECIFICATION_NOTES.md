# Interpretation notes for the vendored UML 2.5.1 XMI

Python translations preserve the source formula's intent. When the XMI's formula
conflicts with its prose or references a nonexistent metaclass, the choice is
recorded here. These choices are project interpretations, not published OMG errata.

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
- Prose-only runtime/layout rules are checked to the extent represented by core UML.
  Missing language facts or occurrence mappings remain explicit unsupported obligations.
