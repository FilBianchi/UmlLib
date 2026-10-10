"""Generate the explicit UML Python module from the vendored OMG XMI."""
from pathlib import Path
import keyword
import xml.etree.ElementTree as ET
import umltools


def generate():
    declarations = {}
    lines = [
        '"""UML 2.5.1 classes generated from umltools/data/UML.xmi.',
        '',
        'Regenerate with python generate_uml.py. Runtime semantics are provided',
        'by umltools; see SEMANTIC_COVERAGE.md for remaining requirements.',
        '"""',
        'from __future__ import annotations',
        'from enum import Enum',
        'from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError',
        'from umltools.semantics import operation as _operation',
        'from umltools.native import NativeNotImplemented',
        '',
    ]
    for name, literals in umltools.ENUMERATIONS.items():
        start = len(lines)
        lines.extend([f'class {name}(Enum):'])
        lines.extend(f'    {literal + "_" if keyword.iskeyword(literal) else literal} = {literal!r}' for literal in literals)
        lines.append('')
        declarations[name] = lines[start:]

    emitted = set()

    def emit(name):
        if name in emitted:
            return
        cls = umltools.REGISTRY[name]
        bases = [base.__name__ for base in cls.__bases__]
        for base in bases:
            if base != 'UmlElement':
                emit(base)
        start = len(lines)
        lines.extend([f'class {name}({", ".join(bases)}):',
                      f'    """UML metaclass {name}."""',
                      f'    __spec__ = SPECIFICATIONS[{name!r}]'])
        primitives = {'String': 'str', 'Boolean': 'bool', 'Integer': 'int', 'Real': 'float', 'UnlimitedNatural': 'int'}
        for prop in umltools.SPECIFICATIONS[name].properties.values():
            python_name = prop.name + '_' if keyword.iskeyword(prop.name) else prop.name
            annotation = primitives.get(prop.type, prop.type or 'object')
            annotation = f'list[{annotation}]' if prop.upper is None or prop.upper > 1 else f'{annotation} | None'
            lines.append(f'    {python_name}: {annotation}')
            if python_name != prop.name:
                lines.extend([f'    @property', f'    def {python_name}(self):', f'        return getattr(self, {prop.name!r})',
                              f'    @{python_name}.setter', f'    def {python_name}(self, value):', f'        setattr(self, {prop.name!r}, value)'])
        for operation in umltools.SPECIFICATIONS[name].operations:
            # Retain the runtime's property/operation name collision policy.
            if operation in cls.__dict__ and callable(cls.__dict__[operation]):
                python_name = operation + '_' if keyword.iskeyword(operation) else operation
                lines.extend([f'    def {python_name}(self, *args, **kwargs):',
                              '        try:',
                              f'            return _operation(self, {name!r}, {operation!r}, args, kwargs)',
                              '        except NativeNotImplemented as error:',
                              '            raise UnsupportedSemanticsError(str(error)) from error'])
        for property_name, descriptor in cls.__dict__.items():
            if isinstance(descriptor, property) and property_name in cls.properties():
                lines.extend(['    @property', f'    def {property_name}(self):',
                              f'        return UmlElement.__getattr__(self, {property_name!r})'])
        lines.append('')
        declarations[name] = lines[start:]
        emitted.add(name)

    for name in umltools.SPECIFICATIONS:
        emit(name)
    names = list(umltools.ENUMERATIONS) + list(umltools.SPECIFICATIONS)
    lines.extend([f'__all__ = {names!r}', '',
                  '_registry = {name: globals()[name] for name in __all__}',
                  'for _name in __all__:',
                  '    globals()[_name].__registry__ = _registry',
                  'del _name', ''])
    root = Path(__file__).parent
    package = root / 'Uml'
    package.mkdir(exist_ok=True)
    groups = {}
    for name, spec in umltools.SPECIFICATIONS.items():
        groups.setdefault(spec.package, []).append(name)
    tree = ET.parse(root / 'umltools' / 'data' / 'UML.xmi').getroot()
    parents = {child: parent for parent in tree.iter() for child in parent}
    for node in tree.iter():
        if node.get(umltools.specification.XMI+'type') == 'uml:Enumeration':
            groups.setdefault(parents[node].get('name'), []).append(node.get('name'))
    classifier_packages = {name: group for group, members in groups.items() for name in members}
    facade = ['"""Generated classifier registry; declarations live in UML packages."""']
    for group, members in groups.items():
        folder = package / group
        folder.mkdir(exist_ok=True)
        (folder / '__init__.py').write_text(f'"""UML 2.5.1 {group} package."""\nfrom importlib import import_module\n\n__all__ = {members!r}\n\ndef __getattr__(name):\n    if name not in __all__: raise AttributeError(name)\n    value = getattr(import_module("._" + name, __name__), name)\n    globals()[name] = value\n    return value\n', encoding='utf-8')
        for name in members:
            header = ['from __future__ import annotations', 'from enum import Enum',
                      'from umltools import UmlElement, SPECIFICATIONS, UnsupportedSemanticsError',
                      'from umltools.semantics import operation as _operation',
                      'from umltools.native import NativeNotImplemented']
            if name in umltools.SPECIFICATIONS:
                for base in umltools.REGISTRY[name].__bases__:
                    if base is not umltools.UmlElement:
                        header.append(f'from ..{classifier_packages[base.__name__]}._{base.__name__} import {base.__name__}')
            (folder / f'_{name}.py').write_text('\n'.join(header + [''] + declarations[name]), encoding='utf-8')
            facade.append(f'from .{group}._{name} import {name}')
    facade.extend([f'__all__ = {names!r}', '_registry = {name: globals()[name] for name in __all__}',
                   'for _name in __all__:', '    globals()[_name].__registry__ = _registry', 'del _name', ''])
    (package / '_classes.py').write_text('\n'.join(facade), encoding='utf-8')
    (package / '__init__.py').write_text('"""UML 2.5.1 organized by its specification packages."""\nfrom ._classes import *\nfrom . import '+', '.join(groups)+'\n\n# Convenient singular alias; StateMachines is the OMG package name.\nStateMachine = StateMachines\n', encoding='utf-8')
    (root / 'UML.py').write_text('"""Compatibility facade; new code may use import Uml."""\nfrom Uml._classes import *\nfrom Uml._classes import __all__\n', encoding='utf-8')


if __name__ == '__main__':
    generate()
