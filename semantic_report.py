"""Inventory explicit Python translations; registration is not conformance."""
from pathlib import Path
import json
import ast
import xml.etree.ElementTree as ET
from collections import Counter
from importlib.resources import files
from umltools import SPECIFICATIONS, REGISTRY
from umltools.native import OPERATIONS, CONSTRAINTS, DERIVATIONS
from umltools.specification import XMI, reference
from umltools.contracts import SIGNATURE_INTERPRETATIONS, multiplicity
from umltools.static_requirements import REQUIREMENTS, SUPPLEMENTAL_QUERIES


AUDIT_LIMITS = {
    **SIGNATURE_INTERPRETATIONS,
    'NamedElement.allOwningPackages': 'A source null in the non-Package branch is normalized to the empty collection required by its signature.',
    'OpaqueExpression.result': 'The XMI body selects the first parameter, even if it is not the return parameter. This differs from the property description; XMI behavior is preserved.',
    'DurationConstraint-firstEvent': 'The source defaults to unordered and unique Boolean values. Repeated first-event flags collapse; ordered event-pair interpretation is unresolved.',
    'DurationObservation-firstEvent': 'The source defaults to unordered and unique Boolean values. Repeated first-event flags collapse; ordered event-pair interpretation is unresolved.',
    'Classifier.directlyUsedInterfaces': 'The XMI traverses supplierDependency/clients; Python follows the Usage description and selects client Usage dependencies and Interface suppliers. Project interpretation remains a source divergence.',
    'Property.binding_to_attribute': 'The XMI casts ts.formal itself to Property although formal is a TemplateParameter. Python checks formal.parameteredElement against the attribute requirement.',
    'Property.isCompatibleWith': 'The source refers to the nonexistent TypeElement; Python uses TypedElement.',
    'Property.isConsistentWith': 'The source upper-bound clause repeats lowerBound; Python uses upperBound according to the description.',
    'ParameterSet.two_parameter_sets': 'The formula compares every pair including a set to itself and uses size on the object. Python compares distinct sets and their parameter memberships according to the description.',
    'Package.makesVisible': 'The source compares importedElement to a VisibilityKind and uses notEmpty on Booleans. Python follows the prose and explicit public-import visibility; private imports are not reexported.',
    'Package.containingProfile': 'The recursive XMI body has no root/null guard. Python returns null at an unowned non-Profile Package, matching the optional result signature.',
    'ConnectorEnd.multiplicity': 'The unconditional formula passes an absent definingEnd to compatibleWith. Python follows the prose: an untyped connector has no association-end bound to constrain it.',
    'Port.encapsulated_owner': 'The null=null formula admits unowned ports. Python follows the ownership description and requires an EncapsulatedClassifier owner.',
    'CollaborationUse.connectors': 'The XMI chooses an arbitrary structuredClassifier association end. Python prefers the owning CollaborationUse classifier when represented, otherwise requires one shared context; ambiguous unowned uses remain unsupported.',
    'Behavior.feature_of_context_classifier': 'The unguarded formula rejects absent specifications although the reference is optional. Python checks context membership only for specified methods.',
    'Behavior.behavioredClassifier.precondition': 'The precondition references the classifier-finding body rather than a Boolean predicate. Python implements the finder and its argument contract; the malformed precondition is not treated as a Boolean proof.',
    'FunctionBehavior.types_of_parameters': 'The source requires exact DataType parameters, excluding PrimitiveType/Enumeration despite broader DataType wording. Python preserves isTypeOf; nested attributes use isKindOf as declared.',
    'ProtocolStateMachine.deep_or_shallow_history': 'The source checks top-level regions only. Python applies the machine-wide prohibition in the prose to nested owned regions as well.',
    'ProtocolStateMachine.entry_exit_do': 'The source checks top-level states only. Python checks states in every nested owned region according to the machine-wide prose.',
    'ProtocolStateMachine.protocol_transitions': 'The source checks top-level regions only. Python checks exact ProtocolTransition types in every nested owned region.',
    'Vertex.containingStateMachine': 'The source omits entry/exit points owned by composite States. Python follows the represented State owner to its containing machine.',
    'Region.isRedefinitionContextValid': 'The source references nonexistent State.redefinedState. Python uses the inherited redefinedVertex link and checks that its target is a State.',
    'Vertex.isConsistentWith': 'The operation has duplicate State-prefixed XMI identifiers and refers to an undeclared redefinedElement. Python uses the redefiningElement argument and the represented owner redefinition relation.',
    'StateMachine.ancestor': 'The source top-level branch reverses the direction described in prose. Python tests whether s2 encloses s1, including equality.',
    'Vertex.isContainedInRegion': 'The source recursion tests the queried region instead of progressing through the vertex containers. Python walks the actual enclosing regions.',
    'Pseudostate.transitions_outgoing': 'The source pairs a transition with itself. Python checks distinct transition pairs as the any-pair prose requires.',
    'Pseudostate.transitions_incoming': 'The source pairs a transition with itself. Python checks distinct transition pairs as the any-pair prose requires.',
    'Region.belongsToPSM': 'An unowned region vacuously satisfies the implication in the body. Python requires a represented containing machine; missing ownership remains invalid.',
    'Node.internal_structure': 'The source tests Property parts as Node objects, which rejects every actual part. Python checks part.type according to the Node internal-structure description.',
    'UseCase.no_association_to_use_case': 'The source subject cardinality does not rule out overlapping subject sets. Python rejects associations between distinct UseCases sharing any subject, according to the prose; cases with no subjects share none.',
    'Actor.associations': 'The source uses the opposite Property.class attribute owner rather than its endpoint type. Python checks the opposite end type and preserves the source prohibition on Behavior endpoints.',
    'InformationFlow.sources_and_targets_kind': 'The unqualified kind tests in the source refer to the flow instead of the endpoint. Python tests each endpoint and excludes InstanceSpecifications classified by Relationships.',
    'InformationItem.has_no': 'The source checks features/generalizations but omits associations. Python also checks Association end types in the model extent according to the prose.',
    'InformationItem.not_instantiable': 'The source checks isAbstract only. Python additionally rejects represented InstanceSpecifications classified by this item, according to the prose.',
    'InformationItem.sources_and_targets': 'Python preserves the source direction: flows conveying a represented InformationItem must use subsets of the sources/targets of flows conveying self. The representation wording in the description is ambiguous and remains a source interpretation to resolve.',
    'Gate.isInsideCF': 'The source implication vacuously returns true without an opposite end or CombinedFragment. Python follows the query description and returns false when these prerequisites are absent.',
    'Gate.isOutsideCF': 'The source implication vacuously returns true without an opposite end or CombinedFragment. Python requires both and represented surrounding ownership, according to the query description.',
    'Gate.matches': 'Python parenthesizes the directional implications so that all name, message-sort and signature checks apply together, according to the query description.',
    'Gate.outside_cf_gate_distinguishable': 'The source counts inside gates as well. Python compares outside gates only, as the prose requires; inside/outside pairs may share the matching name.',
    'Gate.outside_cf_matched': 'The alt branch does not use its operand variable and tests an enclosing-fragment relation that misses the operand. Python requires one matching inside gate per operand as the prose specifies.',
    'Message.messageKind': 'The source body recursively returns the property itself. Python derives complete/lost/found/unknown from represented send and receive ends.',
    'Message.signature_is_signal': 'The source selects inheritedMember only. Python matches allAttributes including owned attributes according to the signal-signature description.',
    'MessageEnd.enclosingFragment': 'The source returns null for an unclassified Gate. Python returns an empty collection matching the result signature.',
    'ActionInputPin.no_control_or_object_flow': 'The source unions fromAction.incoming with the receiving pin outgoing. Python checks fromAction.outgoing as the producer-isolation prose requires.',
    'ObjectNode.input_output_parameter': 'The source repeats inputParameters in its final type check. Python checks output type conformance toward the ObjectNode type as required by the prose; this remains a source divergence.',
    'DecisionNode.parameters': 'The source counts non-return parameters. Python requires exactly one return parameter according to the prose.',
    'DecisionNode.decision_input_flow_incoming': 'The source requires incoming to contain null for an absent optional decisionInputFlow. Python applies the membership check only when that flow exists.',
    'ActivityPartition.represents_property': 'The source tests the partition owner against the represented classifier. Python tests the represented Property owner as required by the prose.',
    'LinkEndCreationData.insertAt_pin': 'The source not isReplaceAll=false reverses the guard. Python requires an insertion pin when an ordered end is not replacing all values, according to the prose.',
    'ConditionalNode.clause_no_predecessor': 'The source closure rejects ordinary acyclic predecessors within the same node. Python rejects predecessor cycles, preserving the project interpretation used for clause sequencing.',
    'LinkEndCreationData.allPins': 'The source including(insertAt) includes null when the optional insertion pin is absent. Python omits absent pins, matching the description and non-null result element contract.',
    'LinkEndDestructionData.allPins': 'The source including(destroyAt) includes null when the optional destruction pin is absent. Python omits absent pins, matching the description and non-null result element contract.',
}
CONTEXT_LIMITS = {
    'InformationFlow.must_conform': 'Nominal endpoint conformance, distinct undirected channel sides and directed activity/message channels are checked as a project interpretation of the prose-only rule. Gate endpoints require explicit mappings; external lost/found endpoints remain unsupported. Runtime delivery is not proved.',
    'InteractionConstraint.minint_non_negative': 'Represented Integer values are checked. Unknown numeric expressions require an evaluator and remain unsupported; wrong computable literal kinds remain invalid.',
    'InteractionConstraint.maxint_positive': 'Represented Integer values are checked. Unknown numeric expressions require an evaluator and remain unsupported; wrong computable literal kinds remain invalid.',
    'InteractionConstraint.maxint_greater_equal_minint': 'Represented Integer bounds are compared. Unknown numeric expressions require an evaluator and remain unsupported.',
    'Message.arguments': 'Constants and represented wildcard values are checked. Foreign expression constancy/references require trusted analyzer facts.',
    'InteractionUse.arguments_are_constants': 'Foreign expression constancy/references require trusted analyzer facts; no arbitrary language execution is supplied.',
    'ObjectFlow.same_upper_bounds': 'Represented UnlimitedNatural bounds are compared along object-flow paths through ControlNodes. Unknown numeric expressions require an evaluator; invalid computable literal kinds are diagnosed.',
    'ObjectFlow.target': 'Constant Integer weights are compared with downstream bounds. Unknown constancy requires analyzer facts; known nonconstant weights are outside this rule, while unevaluated constants remain unsupported.',
    'ReduceAction.input_type_is_collection': 'Multivalued pins represent token collections. A single token needs a registered domain collection type; missing collection-type evidence remains unsupported.',
    'TimeEvent.when_non_negative': 'TimeExpression has no integerValue override in the XMI. Python checks represented computable expr values; foreign expressions/observations require numeric evaluation evidence and remain unsupported. No clock or scheduler is executed.',
}
CONTEXTUAL = {
    'Constraint.no_side_effects', 'MultiplicityElement.value_specification_no_side_effects',
    'MultiplicityElement.value_specification_constant', 'Constraint.boolean_value',
}
PARTIAL = {
    'PackageMerge': 'The model represents receiving/merged Package links. The normative reconciliation/merge algorithm is not implemented.',
    'ProfileApplication-isStrict': 'Strict availability views and checked creation support UML metaclass references, imported profiles, extended subtypes and conflicting filters. Direct constructors remain available for general model editing. Non-UML metaclasses need an adapter; UI presentation and CMOF interoperability remain open.',
    'Stereotype': 'Runtime typed tags support effective inherited/redefined properties, literal defaults, bounds, readonly values, enumerations, profile Class/DataType objects, binary navigable inverses, composition and deletion. Model-defined primitive lexical values retain exact type identity; Python semantics require explicit per-definition codecs. User constraints use trusted Python callbacks or Boolean literals, never arbitrary OCL execution. Derived/general default evaluators, association-owned runtime navigation, full CMOF serialization and exhaustive profile semantics remain open.',
    'ProtocolConformance': 'Specific/general machine links are represented. Behavioral protocol-conformance proof is not implemented.',
    'DeploymentTarget-deployedElement': 'The XMI query retains its Artifact-only filter. The supplemental deployed_elements resolver expands direct manifestations of modeled Artifact classifiers/instances. Nested-artifact, inherited-manifestation, slot and runtime-copy semantics remain open.',
    'DeploymentSpecification-deployed_elements': 'The XMI predicate retains the Artifact-only derivation. validate() additionally checks prose:DeploymentSpecification.configured_instance_elements using modeled Artifact instances. Nested-artifact and runtime-copy semantics remain open.',
    'Continuation-same_name': 'Peer traversal uses context-owned Interactions and role identity with literal selector kind/value. A complete census of every Interaction sharing context and arbitrary domain selector equivalence remains open.',
    'Message-signature_is_operation_reply': 'The XMI predicate is preserved, including vacuous direct values. validate() additionally enforces prose:Message.reply_argument_types on direct typed values, first expression operands and wildcards; arbitrary expression evaluation remains outside this check.',
    'Message-sending_receiving_message_event': 'The check uses represented ordered fragment containment with nested fragments visited before following siblings. A full partial-order semantics for parallel/alternative operands and GeneralOrdering is not implemented.',
    'InteractionConstraint-dynamic_variables': 'Trusted reference facts are checked against represented covered lifeline roles/types, interaction parameters/context attributes and read-only Properties. Full runtime ownership/global/write-once semantics remains a project approximation.',
    'InteractionConstraint-global_data': 'Trusted reference facts and represented read-only Properties are supported. Arbitrary domain global/write-once storage semantics is not represented by core UML and is not proved.',
    'InteractionOperand-guard_contain_references': 'Trusted guard reference facts are checked against represented operand coverage/context. General domain-global and write-once facts remain incomplete.',
    'InteractionOperand-guard_directly_prior': 'Guard composite ownership is checked. Graphical placement immediately above a fragment requires UMLDI/layout semantics and is not proved.',
    'ObjectNode-input_output_parameter': 'Input/output counts, multiplicities and nominal type variance are checked (with a documented source-body correction). Absence of side effects of the selection Behavior is not proved.',
    'ObjectFlow-input_and_output_parameter': 'The XMI count/bounds predicate is preserved. validate() additionally enforces selection input/output types through prose:ObjectFlow.selection_types. Behavior purity remains an external evidence obligation.',
    'ObjectFlow-transformation_behavior': 'The XMI count predicate is preserved. validate() additionally enforces upstream/input and output/downstream conformance through prose:ObjectFlow.transformation_types. Behavior purity remains an external evidence obligation.',
    'DecisionNode-two_input_parameters': 'The XMI count predicate is preserved. validate() additionally enforces ordered regular/decision-flow input types through prose:DecisionNode.input_types; unrepresented token types remain unsupported.',
    'DecisionNode-incoming_control_one_input_parameter': 'The XMI count predicate is preserved. validate() additionally enforces decisionInputFlow token-type conformance through prose:DecisionNode.input_types; unrepresented types remain unsupported.',
    'DecisionNode-incoming_object_one_input_parameter': 'The XMI count predicate is preserved. validate() additionally enforces the sole object input type through prose:DecisionNode.input_types; unrepresented types remain unsupported.',
}


def source_text(node):
    return {'descriptions': [c.get('body', c.findtext('body', '')) for c in node.findall('ownedComment')],
            'expressions': [{'language': s.findtext('language', ''), 'body': s.findtext('body', '')}
                            for s in node.findall('specification')]}


def parameter_signature(node):
    low, high = multiplicity(node)
    return {'id': node.get(XMI+'id'), 'name': node.get('name'), 'direction': node.get('direction', 'in'),
            'type': reference(node, 'type'), 'lower': low, 'upper': high,
            'ordered': node.get('isOrdered', 'false') == 'true', 'unique': node.get('isUnique', 'true') == 'true'}


def linked_examples():
    """Read explicit rule/test links; registration or test counts are not a proof."""
    examples = {}
    for path in sorted(Path(__file__).parent.joinpath('tests').glob('test_*.py')):
        tree = ast.parse(path.read_text(encoding='utf-8'))
        for cls in (n for n in tree.body if isinstance(n, ast.ClassDef)):
            for method in (n for n in cls.body if isinstance(n, ast.FunctionDef)):
                for decorator in method.decorator_list:
                    if not isinstance(decorator, ast.Call) or not isinstance(decorator.func, ast.Name) or decorator.func.id != 'verifies': continue
                    for argument in decorator.args:
                        if not isinstance(argument, ast.Constant) or not isinstance(argument.value, str):
                            raise ValueError('Rule/test links must use literal specification identifiers')
                        examples.setdefault(argument.value, []).append(f'{path.stem}.{cls.name}.{method.name}')
    return {rule: sorted(set(tests)) for rule, tests in examples.items()}


def report():
    examples = linked_examples()
    with files('umltools.data').joinpath('UML.xmi').open('rb') as stream:
        root = ET.parse(stream).getroot()
    source = {n.get(XMI+'id'): n for n in root.iter() if n.get(XMI+'id')}
    source_id_counts = Counter(n.get(XMI+'id') for n in root.iter() if n.get(XMI+'id'))
    parents = {child: parent for parent in root.iter() for child in parent}
    records = []
    for spec in SPECIFICATIONS.values():
        for category, definitions, translations in [('operation', spec.operations, OPERATIONS), ('constraint', spec.constraints, CONSTRAINTS)]:
            for name, definition in definitions.items():
                identifier = f'{spec.name}.{name}'
                function = translations.get(identifier)
                abstract = category == 'operation' and ET.fromstring(definition).get('isAbstract') == 'true'
                status = 'abstract declaration' if abstract else 'native Python' if function else 'not translated'
                xmi_id = ET.fromstring(definition).get(XMI+'id') if category == 'operation' else f'{spec.name}-{name}'
                record = {'id': xmi_id, 'name': identifier, 'package': spec.package, 'kind': category, 'status': status}
                node = ET.fromstring(definition) if category == 'operation' else source[xmi_id]
                record.update(source_text(node))
                if category == 'operation':
                    record['signature'] = [parameter_signature(p) for p in node.findall('ownedParameter')]
                    record['body_conditions'] = [dict(id=r.get(XMI+'id'), **source_text(r)) for r in node.findall('ownedRule') if r.get('name') == 'spec']
                if function: record['implementation'] = f'{function.__module__}.{function.__name__}'
                record['verification'] = 'linked behavioral examples' if identifier in examples else 'no linked behavioral examples'
                if identifier in examples: record['tests'] = examples[identifier]
                records.append(record)
                if category == 'operation':
                    for condition_kind in ('precondition', 'postcondition'):
                        for condition in node.findall(condition_kind):
                            condition_id = condition.get(XMI+'idref')
                            records.append({'id': condition_id, 'name': identifier + '.' + condition_kind,
                                            'operation': identifier, 'package': spec.package, 'kind': condition_kind,
                                            'status': 'query obligation', **source_text(next((r for r in node.findall('ownedRule') if r.get(XMI+'id') == condition_id), source[condition_id]))})
        for prop in spec.properties.values():
            derived = prop.flags.get('isDerived') == 'true'
            if not derived: status = 'runtime structural contract'
            elif prop.id in DERIVATIONS or prop.id in ('Element-owner', 'Element-ownedElement', 'NamedElement-namespace'):
                status = 'native Python'
            elif prop.flags.get('isDerivedUnion') == 'true': status = 'structural union'
            else:
                owner = next((base.__dict__['__spec__'] for base in REGISTRY[spec.name].__mro__ if '__spec__' in base.__dict__ and prop.name in base.__dict__['__spec__'].operations), None)
                status = 'native Python' if owner and f'{owner.name}.{prop.name}' in OPERATIONS else 'not translated'
            records.append({'id': prop.id, 'name': spec.name + '.' + prop.name, 'package': spec.package,
                            'kind': 'derived property' if derived else 'structural property', 'status': status,
                            'type': prop.type, 'lower': prop.lower, 'upper': prop.upper, 'default': prop.default,
                            'ordered': prop.flags.get('isOrdered', 'false') == 'true',
                            'unique': prop.flags.get('isUnique', 'true') == 'true',
                            'readonly': prop.flags.get('isReadOnly', 'false') == 'true',
                            'aggregation': prop.flags.get('aggregation', 'none'),
                            'association': prop.flags.get('association'), 'subsets': prop.subsets, 'redefines': prop.redefines,
                            **source_text(source[prop.id])})
        records.append({'id': spec.name, 'name': spec.name, 'package': spec.package, 'kind': 'class description',
                        'status': 'prose review obligation', **source_text(source[spec.name])})
    inventoried = {r['id'] for r in records}
    for identifier, node in source.items():
        node_type = node.get(XMI+'type')
        if identifier in inventoried or node_type not in ('uml:Property', 'uml:Enumeration'): continue
        container = parents[node]
        package = container
        while package.get(XMI+'type') != 'uml:Package' and package in parents: package = parents[package]
        common = {'id': identifier, 'package': package.get('name', ''), **source_text(node)}
        if node_type == 'uml:Enumeration':
            records.append(dict(common, kind='enumeration', status='generated enumeration',
                                literals=[n.get('name') for n in node.findall('ownedLiteral')]))
        else:
            low, high = multiplicity(node)
            records.append(dict(common, kind='association-owned property', status='inverse relationship obligation',
                                name=node.get('name'), type=reference(node, 'type'), lower=low, upper=high,
                                ordered=node.get('isOrdered', 'false') == 'true', unique=node.get('isUnique', 'true') == 'true',
                                association=node.get('association'), aggregation=node.get('aggregation', 'none'),
                                subsets=[n.get(XMI+'idref') for n in node.findall('subsettedProperty')],
                                redefines=[n.get(XMI+'idref') for n in node.findall('redefinedProperty')]))
    for category, definitions in (('supplemental requirement', REQUIREMENTS), ('supplemental query', SUPPLEMENTAL_QUERIES)):
        for identifier, definition in definitions.items():
            records.append(dict(id=identifier, name=identifier, package=SPECIFICATIONS[definition['owner']].package,
                                kind=category, status='native Python', descriptions=[definition['description']], expressions=[],
                                normative_reference=definition['source'],
                                implementation=definition['function'].__module__+'.'+definition['function'].__name__))
    counts = {category: dict(Counter(record['status'] for record in records if record['kind'] == category))
              for category in sorted({record['kind'] for record in records})}
    known = {key for record in records for key in (record.get('name'), record['id']) if key}
    if set(examples) - known: raise ValueError(f'Tests reference unknown specification rules: {sorted(set(examples) - known)}')
    for record in records:
        name = record.get('name')
        tests = sorted(set(examples.get(name, []) + examples.get(record['id'], [])))
        record['tests'] = tests
        if record['kind'] == 'structural property':
            record['structural_sweeps'] = [
                'test_structural_contracts.StructuralContractCases.test_all_effective_stored_declarations_defaults_and_wrong_types',
                'test_structural_contracts.StructuralContractCases.test_all_stored_setters_accept_values_of_the_declared_type']
        record['verification'] = 'linked behavioral examples' if tests else 'no linked behavioral examples'
        record['review'] = 'verified in linked examples' if tests else 'needs review'
        key = record['id'] if record['id'] in AUDIT_LIMITS else name
        if key in AUDIT_LIMITS:
            record['review'], record['limitation'] = 'source inconsistency', AUDIT_LIMITS[key]
        if name in CONTEXTUAL:
            record['review'] = 'context dependent'
            record['limitation'] = 'Foreign expressions require trusted analyzer facts or a declared static Boolean type; execution is not verified.'
        if record['id'] in PARTIAL:
            record['review'], record['limitation'] = 'partial', PARTIAL[record['id']]
        if name in CONTEXT_LIMITS:
            record['review'], record['limitation'] = 'context dependent', CONTEXT_LIMITS[name]
        record['source'] = 'umltools/data/UML.xmi#' + record.get('normative_reference', record['id'])
        record['static_supplements'] = [identifier for identifier, definition in {**REQUIREMENTS, **SUPPLEMENTAL_QUERIES}.items()
                                       if record['id'] in (definition['source'], *definition.get('additional_sources', ())) and identifier != record['id']]
        if source_id_counts.get(record['id'], 0) > 1:
            record['source_id_ambiguous'] = True
            record['source_disambiguation'] = record.get('name')
    package_audit = {}
    for package in ('CommonStructure', 'Values', 'Classification', 'SimpleClassifiers', 'Packages', 'StructuredClassifiers', 'CommonBehavior', 'StateMachines', 'Activities', 'Actions', 'Interactions', 'UseCases', 'Deployments', 'InformationFlows'):
        definitions = [r for r in records if r['package'] == package]
        counts_by_kind = {category: {'declared': sum(r['kind'] == category for r in definitions),
                                    'with_examples': sum(r['kind'] == category and bool(r['tests']) for r in definitions)}
                          for category in ('constraint', 'operation', 'derived property', 'precondition')}
        package_audit[package] = {'invariants': counts_by_kind['constraint']['declared'],
                                  'invariants_with_examples': counts_by_kind['constraint']['with_examples'],
                                  'definitions': counts_by_kind}
    return {'meaning': 'Implementation inventory and explicitly linked behavioral examples, not proof of complete semantic conformance. No linked examples does not mean no tests exist; earlier tests have not all been linked. Opaque expressions and facts absent from core UML remain explicit validation obligations.',
            'scope': 'Declared core class/property/operation metadata, enumerations, association-owned ends, class invariants, pre/postconditions and XMI descriptions. Additional normative PDF prose still needs separate requirement decomposition; this is not a complete census of every normative UML requirement.',
            'counts': counts, 'verification_counts': dict(Counter(record.get('verification', 'no linked behavioral examples') for record in records)),
            'review_counts': dict(Counter(record['review'] for record in records)), 'package_audit': package_audit,
            'duplicate_source_ids': {identifier: count for identifier, count in source_id_counts.items() if count > 1},
            'definitions': records}


if __name__ == '__main__':
    result = report()
    Path(__file__).with_name('semantic-report.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result['counts']))
