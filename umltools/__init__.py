"""UML 2.5.1 metamodel. Semantic coverage is reported explicitly."""
from enum import Enum
from contextvars import ContextVar
from weakref import WeakSet
from .specification import load, property_refines, property_redefines, property_associations
from .collections import UmlCollection
from .contracts import OperationResultError, validate_item
from .lifecycle import DeletedElementError, DeletionRestrictedError
from .model_session import ModelSession, current_session
from .native import NativeNotImplemented, check
from .semantics import derive, operation
from .evaluation_context import profile_evaluation

SPECIFICATIONS, ENUMERATIONS = load()
REGISTRY = {}
_mutation = ContextVar('uml_mutation', default=None)

class UnsupportedSemanticsError(NotImplementedError):
    pass

class UmlElement:
    __registry__ = REGISTRY
    __instances__ = WeakSet()
    def __init__(self, **values):
        if profile_evaluation.get(): raise ValueError('Cannot create elements during constraint evaluation')
        if self.__spec__.abstract:
            raise TypeError(f'{type(self).__name__} is abstract')
        self._values = {}
        self._container = None
        self._deleted = False
        self._extent = current_session.get()
        transaction = _mutation.get()
        root = transaction is None
        if root:
            transaction = {'snapshots': {}, 'active': set()}
            token = _mutation.set(transaction)
        try:
            for key, value in values.items(): setattr(self, key, value)
        except Exception:
            if root: self._rollback(transaction)
            raise
        finally:
            if root: _mutation.reset(token)
        self.__instances__.add(self)
        if self._extent is not None: self._extent.elements.add(self)

    @classmethod
    def properties(cls):
        result = {}
        for base in reversed(cls.__mro__):
            if '__spec__' in base.__dict__:
                result.update(base.__spec__.properties)
        return result

    def __getattr__(self, name):
        prop = self.properties().get(name)
        if prop is None:
            raise AttributeError(name)
        self._ensure_alive()
        if prop.flags.get('isDerived') == 'true':
            try:
                return derive(self, prop)
            except NativeNotImplemented as error:
                raise UnsupportedSemanticsError(str(error)) from error
        if name not in self._values:
            default = prop.default
            if default is not None:
                default = {'Boolean': lambda: default == 'true', 'Integer': lambda: int(default), 'Real': lambda: float(default),
                           'UnlimitedNatural': lambda: float('inf') if default == '*' else int(default)}.get(prop.type, lambda: self.__registry__[prop.type](default) if prop.type in ENUMERATIONS else default)()
            self._values[name] = UmlCollection(self, name) if prop.upper is None or prop.upper > 1 else default
        return self._values[name]

    def uml_operation(self, owner, name, *args, **kwargs):
        """Invoke a specifically declared query when UML property names collide."""
        try: return operation(self, owner, name, args, kwargs)
        except NativeNotImplemented as error: raise UnsupportedSemanticsError(str(error)) from error

    @property
    def is_deleted(self): return self._deleted

    def _ensure_alive(self):
        if self._deleted: raise DeletedElementError(f'{self.__spec__.name} has been deleted')

    def delete(self, *, cascade=True, on_references='detach'):
        from .lifecycle import delete
        return delete(self, cascade=cascade, on_references=on_references)

    def __setattr__(self, name, value):
        if name.startswith('_'):
            return object.__setattr__(self, name, value)
        if profile_evaluation.get(): raise ValueError('Cannot mutate the model during constraint evaluation')
        transaction = _mutation.get()
        root = transaction is None
        if root:
            transaction = {'snapshots': {}, 'active': set()}
            token = _mutation.set(transaction)
        try:
            key = (id(self), name)
            if key in transaction['active']: return
            if id(self) not in transaction['snapshots']:
                transaction['snapshots'][id(self)] = (self, dict(self._values), {n: list(v) for n, v in self._values.items() if isinstance(v, UmlCollection)}, self._container)
            transaction['active'].add(key)
            try: self._assign(name, value)
            finally: transaction['active'].remove(key)
        except Exception:
            if root:
                self._rollback(transaction)
            raise
        finally:
            if root: _mutation.reset(token)

    def _assign(self, name, value):
        self._ensure_alive()
        if name.endswith('_') and name[:-1] in self.properties():
            name = name[:-1]
        prop = self.properties().get(name)
        if prop is None:
            raise AttributeError(f'Unknown UML property: {name}')
        # A differently named stored ancestor is an alias of its effective
        # redefinition. Route its public setter through the most specific end.
        if prop.flags.get('isDerived') != 'true':
            candidates = [p for n, p in self.properties().items() if n != name and p.flags.get('isDerived') != 'true' and property_redefines(p.id, prop.id)]
            candidates = [p for p in candidates if not any(q.id != p.id and property_redefines(q.id, p.id) for q in candidates)]
            if len(candidates) > 1: raise UnsupportedSemanticsError('Ambiguous stored property redefinition: '+prop.id)
            if candidates and (id(self), candidates[0].name) not in _mutation.get()['active']:
                effective = candidates[0]
                setattr(self, effective.name, value)
                resolved = getattr(self, effective.name)
                if prop.upper is None or prop.upper > 1:
                    existing = self._values.get(name)
                    if isinstance(existing, UmlCollection): existing._data[:] = self._items(resolved)
                    else: self._values[name] = UmlCollection(self, name, self._items(resolved))
                else: self._values[name] = resolved
                return
        if prop.flags.get('isDerived') == 'true' or prop.flags.get('isReadOnly') == 'true':
            raise UnsupportedSemanticsError(f'Write to {prop.id} requires semantic support')
        many = prop.upper is None or prop.upper > 1
        if many and not isinstance(value, (list, tuple, UmlCollection)):
            raise TypeError(f'{name} requires a collection')
        for item in value if many else [value]:
            if many and item is None:
                raise TypeError(f'{name} cannot contain null')
            if item is not None: validate_item(self, item, prop.type)
        values = list(value) if many else self._items(value)
        if many and prop.flags.get('isUnique', 'true') == 'true':
            values = list(dict.fromkeys(values))
        if many and prop.upper is not None and len(values) > prop.upper:
            raise ValueError(f'{name} exceeds upper multiplicity')
        previous = self._items(self._values.get(name))
        if prop.flags.get('aggregation') == 'composite':
            for child in values:
                ancestor = self
                while ancestor is not None:
                    if ancestor is child: raise ValueError('Composite ownership cycle')
                    ancestor = ancestor._container
                if child._container is not None and child._container is not self:
                    raise ValueError('Element already has a composite owner; detach it first')
                for other_name, other_prop in self.properties().items():
                    if other_name != name and other_prop.flags.get('aggregation') == 'composite' and other_prop.flags.get('isDerived') != 'true' and child in self._items(self._values.get(other_name)) and not (property_refines(prop.id, other_prop.id) or property_refines(other_prop.id, prop.id) or any(property_refines(witness.id, prop.id) and property_refines(witness.id, other_prop.id) and child in self._items(self._values.get(witness_name)) for witness_name, witness in self.properties().items())):
                        raise ValueError('Element already occupies another composite property')
            for child in values:
                self._snapshot(child)
                child._container = self
        if many:
            existing = self._values.get(name)
            if isinstance(existing, UmlCollection): existing._data[:] = values
            else: self._values[name] = UmlCollection(self, name, values)
        else:
            self._values[name] = value
        # Synchronize stored supersets. Derived unions compute their members on read.
        # Differently named redefinitions are aliases, not additive subsets. Delay
        # them until primary opposite removal has released prior composite ownership.
        aliases = []
        for other_name, other_prop in self.properties().items():
            if other_name == name or other_prop.flags.get('isDerived') == 'true': continue
            current = self._items(getattr(self, other_name))
            if property_redefines(prop.id, other_prop.id) or property_redefines(other_prop.id, prop.id):
                updated = values
            elif property_refines(prop.id, other_prop.id) or any(property_refines(prop.id, ancestor) for ancestor in other_prop.redefines):
                updated = list(dict.fromkeys(current + values))
            elif property_refines(other_prop.id, prop.id) or any(property_refines(other_prop.id, ancestor) for ancestor in prop.redefines):
                updated = [item for item in current if item in values]
            else: continue
            if updated != current:
                other_many = other_prop.upper is None or other_prop.upper > 1
                if not other_many and len(updated) > 1: raise ValueError('Subset exceeds superset multiplicity')
                assignment = updated if other_many else (updated[0] if updated else None)
                if property_redefines(prop.id, other_prop.id) or property_redefines(other_prop.id, prop.id):
                    aliases.append((other_name, assignment))
                else: setattr(self, other_name, assignment)
        if prop.flags.get('aggregation') == 'composite':
            for child in previous:
                if child not in values and not any(p.flags.get('aggregation') == 'composite' and child in self._items(self._values.get(n)) for n, p in self.properties().items()):
                    self._snapshot(child)
                    child._container = None
        associations = property_associations(prop.id)
        if associations:
            for target in previous + [v for v in values if v not in previous]:
                if not isinstance(target, UmlElement): continue
                # Establish the directly declared opposite before inherited ends.
                # Its subset memberships can witness legitimate shared composites.
                opposites = sorted(target.properties().values(), key=lambda p: p.flags.get('association') != prop.flags.get('association'))
                for opposite in opposites:
                    if property_refines(prop.id, opposite.id) or property_refines(opposite.id, prop.id) or opposite.flags.get('association') not in associations or opposite.flags.get('isDerived') == 'true': continue
                    inverse_many = opposite.upper is None or opposite.upper > 1
                    current = self._items(getattr(target, opposite.name))
                    if target not in values and any(target in self._items(self._values.get(n))
                            and opposite.flags.get('association') in property_associations(p.id)
                            and not (property_redefines(prop.id, p.id) or property_redefines(p.id, prop.id))
                            for n, p in self.properties().items()): continue
                    if target not in values and target._container is self and property_refines(opposite.id, 'Element-owner'): continue
                    updated = [x for x in current if x is not self]
                    if target in values: updated.append(self)
                    setattr(target, opposite.name, updated if inverse_many else (updated[-1] if updated else None))
        for alias_name, assignment in aliases:
            if self._items(getattr(self, alias_name)) != self._items(assignment): setattr(self, alias_name, assignment)

    @staticmethod
    def _rollback(transaction):
        for obj, values, collections, container in transaction['snapshots'].values():
            obj._values = values
            obj._container = container
            for n, contents in collections.items(): obj._values[n]._data[:] = contents

    @staticmethod
    def _snapshot(obj):
        transaction = _mutation.get()
        if id(obj) not in transaction['snapshots']:
            transaction['snapshots'][id(obj)] = (obj, dict(obj._values), {n: list(v) for n, v in obj._values.items() if isinstance(v, UmlCollection)}, obj._container)

    @staticmethod
    def _items(value):
        return list(value) if isinstance(value, (list, tuple, UmlCollection)) else [] if value is None else [value]

    def validate(self, recursive=False):
        """Report structural failures and every unevaluated semantic obligation."""
        self._ensure_alive()
        issues = []
        for name, prop in self.properties().items():
            if prop.flags.get('isDerived') == 'true':
                try: value = getattr(self, name)
                except (UnsupportedSemanticsError, RecursionError):
                    issues.append(('unsupported', prop.id))
                    continue
                except (ValueError, TypeError, AttributeError, IndexError, ZeroDivisionError):
                    issues.append(('invalid derivation', prop.id))
                    continue
            else: value = getattr(self, name)
            if prop.flags.get('isDerived') != 'true' and any(isinstance(target, UmlElement) and target._extent is not self._extent for target in self._items(value)):
                issues.append(('cross session reference', prop.id))
            size = len(value) if isinstance(value, (list, tuple, UmlCollection)) else int(value is not None)
            if size < prop.lower or prop.upper is not None and size > prop.upper:
                issues.append(('multiplicity', prop.id))
        for base in type(self).__mro__:
            spec = base.__dict__.get('__spec__')
            if spec:
                for name in spec.constraints:
                    identifier = f'{spec.name}.{name}'
                    try:
                        if not check(self, identifier): issues.append(('constraint', identifier))
                    except (NativeNotImplemented, UnsupportedSemanticsError, RecursionError):
                        issues.append(('unsupported constraint', identifier))
                    except (TypeError, ValueError, AttributeError, IndexError, ZeroDivisionError):
                        issues.append(('invalid constraint', identifier))
        from .static_requirements import validate_static
        issues.extend(validate_static(self))
        from .stereotypes import validate_applications
        try: issues.extend(validate_applications(self))
        except (NativeNotImplemented, UnsupportedSemanticsError):
            issues.append(('unsupported stereotype application', 'Stereotype.application'))
        except (ValueError, TypeError, AttributeError):
            issues.append(('invalid stereotype application', 'Stereotype.application'))
        if recursive:
            for child in self.ownedElement:
                issues.extend(child.validate(recursive=True))
        return issues

for name, literals in ENUMERATIONS.items():
    REGISTRY[name] = Enum(name, {literal: literal for literal in literals}, module=__name__)

def build(name):
    if name in REGISTRY:
        return REGISTRY[name]
    spec = SPECIFICATIONS[name]
    bases = tuple(build(base) for base in spec.bases) or (UmlElement,)
    bases = tuple(base for base in bases if not any(other is not base and issubclass(other, base) for other in bases))
    namespace = {'__spec__': spec, '__module__': __name__}
    property_names = set(spec.properties)
    for base in bases:
        property_names.update(base.properties())
    for operation in spec.operations:
        if operation in property_names:
            continue
        def unsupported(self, *args, _owner=name, _operation=operation, **kwargs):
            try:
                return globals()['operation'](self, _owner, _operation, args, kwargs)
            except NativeNotImplemented as error:
                raise UnsupportedSemanticsError(str(error)) from error
        namespace[operation] = unsupported
    for property_name in sorted(property_names):
        if any(callable(getattr(base, property_name, None)) for base in bases):
            def read_property(self, _name=property_name): return UmlElement.__getattr__(self, _name)
            namespace[property_name] = property(read_property)
    REGISTRY[name] = type(name, bases, namespace)
    return REGISTRY[name]

for name in SPECIFICATIONS:
    build(name)
globals().update(REGISTRY)
__all__ = list(REGISTRY) + ['UnsupportedSemanticsError', 'OperationResultError', 'DeletedElementError', 'DeletionRestrictedError', 'SPECIFICATIONS']
