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
}
CONTEXTUAL = {
    'Constraint.no_side_effects', 'MultiplicityElement.value_specification_no_side_effects',
    'MultiplicityElement.value_specification_constant', 'Constraint.boolean_value',
}
PARTIAL = {
    'PackageMerge': 'The model represents receiving/merged Package links. The normative reconciliation/merge algorithm is not implemented.',
    'ProfileApplication-isStrict': 'The Boolean is stored, but strict metaclass/visibility restrictions of applied profiles are not enforced by the runtime.',
    'Stereotype': 'Base bindings and declared invariants are implemented. A complete typed tagged-value API and arbitrary user-defined stereotype constraint execution are not implemented.',
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
                node = source[xmi_id]
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
                                            'status': 'query obligation', **source_text(source[condition_id])})
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
    counts = {category: dict(Counter(record['status'] for record in records if record['kind'] == category))
              for category in sorted({record['kind'] for record in records})}
    known = {key for record in records for key in (record.get('name'), record['id']) if key}
    if set(examples) - known: raise ValueError(f'Tests reference unknown specification rules: {sorted(set(examples) - known)}')
    for record in records:
        name = record.get('name')
        tests = sorted(set(examples.get(name, []) + examples.get(record['id'], [])))
        record['tests'] = tests
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
        record['source'] = 'umltools/data/UML.xmi#' + record['id']
    package_audit = {}
    for package in ('CommonStructure', 'Values', 'Classification', 'SimpleClassifiers', 'Packages', 'StructuredClassifiers'):
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
            'definitions': records}


if __name__ == '__main__':
    result = report()
    Path(__file__).with_name('semantic-report.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result['counts']))
