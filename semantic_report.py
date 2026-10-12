"""Inventory explicit Python translations; registration is not conformance."""
from pathlib import Path
import json
import ast
import xml.etree.ElementTree as ET
from collections import Counter
from umltools import SPECIFICATIONS, REGISTRY
from umltools.native import OPERATIONS, CONSTRAINTS, DERIVATIONS
from umltools.specification import XMI


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
                if function: record['implementation'] = f'{function.__module__}.{function.__name__}'
                record['verification'] = 'linked behavioral examples' if identifier in examples else 'no linked behavioral examples'
                if identifier in examples: record['tests'] = examples[identifier]
                records.append(record)
        for prop in spec.properties.values():
            if prop.flags.get('isDerived') != 'true': continue
            if prop.id in DERIVATIONS or prop.id in ('Element-owner', 'Element-ownedElement', 'NamedElement-namespace'):
                status = 'native Python'
            elif prop.flags.get('isDerivedUnion') == 'true': status = 'structural union'
            else:
                owner = next((base.__dict__['__spec__'] for base in REGISTRY[spec.name].__mro__ if '__spec__' in base.__dict__ and prop.name in base.__dict__['__spec__'].operations), None)
                status = 'native Python' if owner and f'{owner.name}.{prop.name}' in OPERATIONS else 'not translated'
            records.append({'id': prop.id, 'package': spec.package, 'kind': 'derived property', 'status': status})
    counts = {category: dict(Counter(record['status'] for record in records if record['kind'] == category)) for category in ('operation', 'constraint', 'derived property')}
    known = {record.get('name') for record in records}
    if set(examples) - known: raise ValueError(f'Tests reference unknown specification rules: {sorted(set(examples) - known)}')
    return {'meaning': 'Implementation inventory and explicitly linked behavioral examples, not proof of complete semantic conformance. No linked examples does not mean no tests exist; earlier tests have not all been linked. Opaque expressions and facts absent from core UML remain explicit validation obligations.',
            'counts': counts, 'verification_counts': dict(Counter(record.get('verification', 'no linked behavioral examples') for record in records)),
            'definitions': records}


if __name__ == '__main__':
    result = report()
    Path(__file__).with_name('semantic-report.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result['counts']))
