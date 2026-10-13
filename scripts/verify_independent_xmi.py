"""Test-only, adapted XMI interchange against pinned PyUML2/PyEcore.

Run in an isolated environment with requirements-interoperability.txt installed.
No independent engine is imported by the library or the regular unit suite.
"""
import argparse
import importlib
import json
from pathlib import Path

from umltools.xmi import XmiDocument, load


REFERENCE_COMMIT = 'bbea7442b2f4ba0870c42c15e4738e86ba90ea49'
VERSIONS = ('2.4.1', '2.5.1')
FIELDS = {
    'Model': ('packagedElement',),
    'Class': ('ownedAttribute', 'ownedConnector', 'generalization'),
    'Interface': (),
    'Association': ('ownedEnd', 'memberEnd'),
    'Property': ('type', 'aggregation', 'lowerValue', 'upperValue'),
    'Port': ('type', 'aggregation', 'isConjugated'),
    'Connector': ('type', 'end'),
    'ConnectorEnd': ('role', 'partWithPort'),
    'Generalization': ('general',),
    'LiteralInteger': ('value',),
    'LiteralUnlimitedNatural': ('value',),
}

# Authored expected graph: names are fixture-local keys, not expected values
# calculated by the engine. Containment is checked independently of references.
EXPECTED = {
    'M': ('Model', None, {'packagedElement': ['Service', 'Base', 'Child', 'Wire']}),
    'Service': ('Interface', 'M', {}),
    'Base': ('Class', 'M', {'ownedAttribute': [], 'ownedConnector': [], 'generalization': []}),
    'Child': ('Class', 'M', {'ownedAttribute': ['part', 'input', 'output'], 'ownedConnector': ['connection'], 'generalization': ['inherits']}),
    'inherits': ('Generalization', 'Child', {'general': 'Base'}),
    'part': ('Property', 'Child', {'type': 'Base', 'aggregation': 'composite', 'lowerValue': 'low', 'upperValue': 'high'}),
    'low': ('LiteralInteger', 'part', {'value': 0}),
    'high': ('LiteralUnlimitedNatural', 'part', {'value': 4}),
    'input': ('Port', 'Child', {'type': 'Service', 'aggregation': 'none', 'isConjugated': False}),
    'output': ('Port', 'Child', {'type': 'Service', 'aggregation': 'none', 'isConjugated': True}),
    'Wire': ('Association', 'M', {'ownedEnd': ['left', 'right'], 'memberEnd': ['left', 'right']}),
    'left': ('Property', 'Wire', {'type': 'Service', 'aggregation': 'none', 'lowerValue': None, 'upperValue': None}),
    'right': ('Property', 'Wire', {'type': 'Service', 'aggregation': 'none', 'lowerValue': None, 'upperValue': None}),
    'connection': ('Connector', 'Child', {'type': 'Wire', 'end': ['first', 'second']}),
    'first': ('ConnectorEnd', 'connection', {'role': 'input', 'partWithPort': None}),
    'second': ('ConnectorEnd', 'connection', {'role': 'output', 'partWithPort': None}),
}


def fixture(version):
    u = importlib.import_module('Uml241' if version == '2.4.1' else 'Uml251')
    doc = XmiDocument.new('M', semantic_version=version)
    with doc.session:
        model = doc.roots[0]
        interface, base, child = u.Interface(name='Service'), u.Class(name='Base'), u.Class(name='Child')
        child.generalization.append(u.Generalization(general=base))
        part = u.Property(name='part', type=base, aggregation=u.AggregationKind.composite,
                          lowerValue=u.LiteralInteger(name='low', value=0),
                          upperValue=u.LiteralUnlimitedNatural(name='high', value=4))
        a, b = u.Port(name='input', type=interface), u.Port(name='output', type=interface, isConjugated=True)
        child.ownedAttribute.extend([part, a, b])
        wire = u.Association(name='Wire', ownedEnd=[u.Property(name='left', type=interface), u.Property(name='right', type=interface)])
        child.ownedConnector.append(u.Connector(name='connection', type=wire,
            end=[u.ConnectorEnd(role=a), u.ConnectorEnd(role=b)]))
        model.packagedElement.extend([interface, base, child, wire])
    return doc


def snapshot(elements, external=False):
    elements = list(elements)
    def label(element):
        cls = element.eClass.name if external else element.__spec__.name
        if cls == 'Generalization':
            return 'inherits'
        if cls == 'ConnectorEnd':
            owner = element.eContainer() if external else element.owner
            return ('first', 'second')[list(owner.end).index(element)]
        return element.name
    by_name = {label(e): e for e in elements}
    if len(by_name) != len(elements) or set(by_name) != set(EXPECTED):
        raise AssertionError('Fixture elements lost, duplicated or added')
    def value(item):
        if item is None or isinstance(item, (bool, int, float, str)):
            return item
        if external and getattr(getattr(item, 'eClass', None), 'name', None) == 'EEnumLiteral':
            return item.name
        if external and hasattr(item, 'eClass'):
            if by_name.get(label(item)) is not item:
                raise AssertionError('Reference does not point to the contained object')
            return label(item)
        if not external and hasattr(item, '__spec__'):
            if by_name.get(label(item)) is not item:
                raise AssertionError('Reference identity differs from contained object')
            return label(item)
        if external and hasattr(item, 'name'):  # PyEcore enum literal
            return item.name
        if not external and hasattr(item, 'value'):  # UmlLib enum
            return item.value
        return [value(v) for v in item]
    result = {}
    for name, element in by_name.items():
        cls = element.eClass.name if external else element.__spec__.name
        owner = element.eContainer() if external else element.owner
        fields = {field: value(getattr(element, field)) for field in FIELDS[cls]}
        result[name] = (cls, label(owner) if owner else None, fields)
    return result


def adapt_namespace(data, target):
    """Only XML dialect adaptation, not semantic UML version conversion."""
    from lxml import etree
    root = etree.fromstring(data)
    source = root.nsmap['uml']
    for node in list(root):
        if etree.QName(node).localname == 'Extension':
            root.remove(node)  # version metadata would contradict the adapted dialect
    # PyEcore does not implement the XMI idref child form. Use its equivalent
    # local-ID reference attribute form, preserving target IDs and order.
    idref = '{' + root.nsmap['xmi'] + '}idref'
    for parent in list(root.iter()):
        for child in list(parent):
            target_id = child.get(idref)
            if target_id is None:
                continue
            if len(child) or set(child.attrib) != {idref} or child.tag.startswith('{'):
                raise ValueError('Reference adaptation would discard XML data')
            previous = parent.get(child.tag, '')
            parent.set(child.tag, (previous + ' ' + target_id).strip())
            parent.remove(child)
        # PyUML2 exposes this UML feature under its Python keyword escape.
        if 'class' in parent.attrib:
            parent.set('class_', parent.attrib.pop('class'))
    data = etree.tostring(root, xml_declaration=True, encoding='utf-8')
    data = data.replace(('xmlns:uml="' + source + '"').encode(), ('xmlns:uml="' + target + '"').encode())
    xmi = root.nsmap['xmi']
    return data.replace(('xmlns:xmi="' + xmi + '"').encode(), b'xmlns:xmi="http://www.omg.org/XMI"')


def verify(output):
    import pyuml2.uml as reference
    from pyecore.resources import ResourceSet, URI
    output.mkdir(parents=True, exist_ok=True)
    results = []
    for version in VERSIONS:
        doc = fixture(version)
        if snapshot(doc.session.elements) != EXPECTED:
            raise AssertionError('UmlLib source graph differs from authored oracle')
        original = output / ('source-' + version + '.xmi')
        doc.save(original)
        rset = ResourceSet()
        rset.metamodel_registry[reference.nsURI] = reference
        try:
            rset.get_resource(URI(str(original.resolve())))
        except Exception as error:
            direct = {'status': 'unsupported', 'error_type': type(error).__name__, 'message': str(error)}
        else:
            direct = {'status': 'readable'}
        adapted = output / ('adapted-' + version + '.uml')
        adapted.write_bytes(adapt_namespace(original.read_bytes(), reference.nsURI))
        rset = ResourceSet()
        rset.metamodel_registry[reference.nsURI] = reference
        resource = rset.get_resource(URI(str(adapted.resolve())))
        model = resource.contents[0]
        if snapshot([model, *model.eAllContents()], external=True) != EXPECTED:
            raise AssertionError('Independent reader changed graph values or identity')
        returned = output / ('returned-' + version + '.uml')
        resource.uri = URI(str(returned.resolve()))
        resource.save()
        restored = load(returned, semantic_version=version)
        if snapshot(restored.session.elements) != EXPECTED:
            raise AssertionError('Independent serialization changed graph values or identity')
        results.append({'semantic_version': version, 'direct_import': direct,
                        'adapted_import_and_return': 'passed', 'elements': len(EXPECTED)})
    report = {'reference': 'pyecore/pyuml2', 'commit': REFERENCE_COMMIT,
              'pyecore': '0.15.2', 'scope': 'adapted structural interchange; not semantic version conformance',
              'results': results}
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('.build-tmp/independent-xmi'))
    verify(parser.parse_args().output)
