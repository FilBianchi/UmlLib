"""Read the vendored OMG metamodel without requiring Qt or network access."""
from dataclasses import dataclass, field
from pathlib import Path
from importlib.resources import files
import xml.etree.ElementTree as ET

XMI = '{http://www.omg.org/spec/XMI/20131001}'
SOURCE_NAME = 'UML.xmi'
PROPERTY_RELATIONS = {}
PROPERTY_REDEFINITIONS = {}
PROPERTY_ASSOCIATIONS = {}


def property_refines(identifier, target, visited=None):
    if identifier == target: return True
    visited = set() if visited is None else visited
    if identifier in visited: return False
    visited = visited | {identifier}
    return any(property_refines(parent, target, visited) for parent in PROPERTY_RELATIONS.get(identifier, ()))


def property_redefines(identifier, target, visited=None):
    if identifier == target: return True
    visited = set() if visited is None else visited
    if identifier in visited: return False
    return any(property_redefines(parent, target, visited | {identifier}) for parent in PROPERTY_REDEFINITIONS.get(identifier, ()))


def property_associations(identifier, visited=None):
    visited = set() if visited is None else visited
    if identifier in visited: return set()
    visited = visited | {identifier}
    own = PROPERTY_ASSOCIATIONS.get(identifier)
    return ({own} if own else set()) | {association for parent in PROPERTY_RELATIONS.get(identifier, ()) for association in property_associations(parent, visited)}

@dataclass
class PropertySpec:
    id: str
    name: str
    type: str | None
    lower: int
    upper: int | None
    flags: dict
    subsets: tuple
    redefines: tuple
    default: str | None

@dataclass
class ClassSpec:
    name: str
    abstract: bool
    bases: tuple
    properties: dict = field(default_factory=dict)
    constraints: dict = field(default_factory=dict)
    operations: dict = field(default_factory=dict)
    package: str = ''

def reference(node, name):
    child = node.find(name)
    return node.get(name) or (None if child is None else child.get(XMI+'idref') or child.get('href', '').split('#')[-1])

def expression(node):
    return tuple((x.get('language') or x.findtext('language') or '', x.get('body') or x.findtext('body') or '') for x in node.findall('.//'+ 'specification') + node.findall('bodyCondition/specification'))


def references(node, name):
    """MOF reference lists may be attributes (2.4.1) or child elements (2.5.1)."""
    return tuple((node.get(name) or '').split()) + tuple(
        child.get(XMI+'idref') or child.get('href','').split('#')[-1]
        for child in node.findall(name))

def load(path=None):
    source = Path(path) if path else files('umltools.data').joinpath(SOURCE_NAME)
    with source.open('rb') as stream:
        root = ET.parse(stream).getroot()
    PROPERTY_RELATIONS.clear()
    PROPERTY_RELATIONS.update({node.get(XMI+'id'): references(node,'subsettedProperty') + references(node,'redefinedProperty') for node in root.iter() if node.get(XMI+'type') == 'uml:Property'})
    PROPERTY_REDEFINITIONS.clear()
    PROPERTY_REDEFINITIONS.update({node.get(XMI+'id'): references(node,'redefinedProperty') for node in root.iter() if node.get(XMI+'type') == 'uml:Property'})
    PROPERTY_ASSOCIATIONS.clear()
    PROPERTY_ASSOCIATIONS.update({node.get(XMI+'id'): node.get('association') for node in root.iter() if node.get(XMI+'type') == 'uml:Property'})
    parents = {child: parent for parent in root.iter() for child in parent}
    classes, enums = {}, {}
    for node in root.iter():
        kind = node.get(XMI+'type')
        if kind == 'uml:Enumeration':
            enums[node.get('name')] = tuple(x.get('name') for x in node.findall('ownedLiteral'))
        if kind != 'uml:Class':
            continue
        spec = ClassSpec(node.get('name'), node.get('isAbstract') == 'true', tuple(reference(x, 'general') for x in node.findall('generalization')))
        spec.package = parents[node].get('name', '')
        for p in node.findall('ownedAttribute'):
            lower, upper, default = p.find('lowerValue'), p.find('upperValue'), p.find('defaultValue')
            high = '1' if upper is None else upper.get('value', '0')
            spec.properties[p.get('name')] = PropertySpec(p.get(XMI+'id'), p.get('name'), reference(p, 'type'), 1 if lower is None else int(lower.get('value', '0')), None if high == '*' else int(high), dict(p.attrib), references(p,'subsettedProperty'), references(p,'redefinedProperty'), None if default is None else default.get('value', 'false' if default.get(XMI+'type') == 'uml:LiteralBoolean' else '0'))
            if default is not None and default.get(XMI+'type') == 'uml:LiteralString':
                spec.properties[p.get('name')].default = default.get('value', '')
        spec.constraints = {x.get('name'): expression(x) for x in node.findall('ownedRule')}
        for p in node.findall('ownedAttribute'):
            default = p.find('defaultValue')
            if default is not None and default.get(XMI+'type') == 'uml:InstanceValue':
                instance = reference(default, 'instance')
                literals = [x for x in root.iter() if x.get(XMI+'id') == instance]
                spec.properties[p.get('name')].default = literals[0].get('name') if literals else None
        spec.operations = {x.get('name'): ET.tostring(x, encoding='unicode') for x in node.findall('ownedOperation')}
        classes[spec.name] = spec
    return classes, enums
