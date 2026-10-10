"""Inventory explicit Python translations; registration is not conformance."""
from pathlib import Path
import json
import xml.etree.ElementTree as ET
from collections import Counter
from umltools import SPECIFICATIONS, REGISTRY
from umltools.native import OPERATIONS, CONSTRAINTS, DERIVATIONS
from umltools.specification import XMI


def report():
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
    return {'meaning': 'Inventory of registered Python definitions, not proof of complete semantic conformance. Opaque language expressions, domain collection types and decomposition mappings can require application-supplied semantic facts; validation reports unsupported obligations explicitly.', 'counts': counts, 'definitions': records}


if __name__ == '__main__':
    result = report()
    Path(__file__).with_name('semantic-report.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result['counts']))
