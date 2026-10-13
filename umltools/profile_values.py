"""Runtime values of profile-defined types, distinct from InstanceSpecification.

Tag collections are immutable snapshots; all edits pass through checked updates.
Foreign derived/default expressions and user constraints need explicit adapters.
"""
from dataclasses import dataclass
from types import MappingProxyType
from weakref import WeakSet, WeakKeyDictionary
from .native import kind, NativeNotImplemented
from .native.constraints_remaining import base_properties
from .contracts import validate_item
from .evaluation_context import profile_evaluation
from .primitive_values import PrimitiveValue

_records = WeakSet()
_constraint_adapters = WeakKeyDictionary()


def defining_profile(classifier):
    current, seen = classifier.owner, set()
    while current is not None:
        if current in seen: raise ValueError('Cyclic profile ownership')
        seen.add(current)
        if kind(classifier, current, 'Profile'): return current
        current = current.owner
    return None


def containing_package(element):
    while element is not None:
        if kind(element, element, 'Package'): return element
        element = element.owner
    return None


@dataclass(frozen=True)
class EnumValue:
    literal: object

    @property
    def name(self):
        self.literal._ensure_alive()
        return self.literal.name


def register_profile_constraint(constraint, predicate):
    if profile_evaluation.get(): raise ValueError('Cannot mutate adapters during constraint evaluation')
    if not kind(constraint, constraint, 'Constraint'): raise TypeError('Expected Constraint')
    constraint._ensure_alive()
    if not callable(predicate): raise TypeError('Expected callable constraint evaluator')
    _constraint_adapters[constraint] = predicate


def unregister_profile_constraint(constraint):
    if profile_evaluation.get(): raise ValueError('Cannot mutate adapters during constraint evaluation')
    _constraint_adapters.pop(constraint, None)


class ProfileObject:
    """An instance of a profile-defined Class/DataType (not a UML instance model)."""
    def __init__(self, classifier, package, *, values=None):
        if not (kind(classifier, classifier, 'Class') or kind(classifier, classifier, 'DataType')) or any(kind(classifier, classifier, n) for n in ('Stereotype','Enumeration','PrimitiveType')):
            raise TypeError('Expected a profile-defined Class or DataType')
        profile = defining_profile(classifier)
        if profile is None: raise ValueError('Classifier must be defined in a Profile')
        if classifier.isAbstract: raise ValueError('Cannot instantiate an abstract profile type')
        from .stereotypes import available_profiles
        package._ensure_alive()
        if not kind(package, package, 'Package'): raise TypeError('Expected Package')
        if profile not in available_profiles(package): raise ValueError('Profile type is unavailable in this package')
        self._init_values(classifier, package)
        self._update(values or {}, initializing=True)
        self._register()

    def _init_values(self, classifier, package):
        if profile_evaluation.get(): raise ValueError('Cannot create profile values during constraint evaluation')
        classifier._ensure_alive()
        self._classifier, self._package = classifier, package
        self._profile = defining_profile(classifier)
        self._values = {}
        self._deleted = False
        self._composite_owner = None
        self._registry_package = None

    def _ensure_alive(self):
        from .lifecycle import DeletedElementError
        if self._deleted: raise DeletedElementError('Profile instance has been deleted')
        self._classifier._ensure_alive()

    @property
    def is_deleted(self): return self._deleted

    @property
    def classifier(self): return self._classifier

    @property
    def package(self):
        return self._composite_owner[0].package if self._composite_owner is not None else self._package

    def _register(self):
        _records.add(self)
        package = self.package
        if self._registry_package is not package:
            if self._registry_package is not None: getattr(self._registry_package, '_profile_instances', set()).discard(self)
            self._registry_package = package
            if package is not None:
                if not hasattr(package, '_profile_instances'): package._profile_instances = set()
                package._profile_instances.add(self)
        for prop, values in self._values.items():
            if prop.isComposite:
                for value in values: value._register()

    def _properties(self):
        self._ensure_alive()
        bases = set(base_properties(self._classifier)) if kind(self._classifier, self._classifier, 'Stereotype') else set()
        return [p for p in self._classifier.allAttributes() if p not in bases and not p.isStatic]

    def _property(self, key):
        props = self._properties()
        matches = [p for p in props if p.name == key] if isinstance(key, str) else [p for p in props if p is key]
        if len(matches) != 1: raise ValueError('Tag key must identify one effective property')
        return matches[0]

    def _item(self, prop, value):
        type_ = prop.type
        if type_ is None: raise ValueError('Tag property has no type')
        type_._ensure_alive()
        if kind(type_, type_, 'PrimitiveType'):
            if isinstance(value,PrimitiveValue):
                if value.classifier is not type_: raise TypeError('Primitive value must use the declared type definition')
                value.classifier._ensure_alive()
                if value.has_semantics: value.to_python()
                if type_.name in ('Boolean','Integer','Real','String','UnlimitedNatural'): return value.to_python()
                return value
            if type_.name not in ('Boolean','Integer','Real','String','UnlimitedNatural'):
                raise NativeNotImplemented('Custom primitive type requires a value adapter')
            validate_item(type_, value, type_.name)
            return value
        if kind(type_, type_, 'Enumeration'):
            if isinstance(value, str):
                matches = [l for l in type_.ownedLiteral if l.name == value]
                if len(matches) != 1: raise ValueError('Enumeration name must identify one literal')
                value = EnumValue(matches[0])
            elif kind(type_, value, 'EnumerationLiteral'): value = EnumValue(value)
            if not isinstance(value, EnumValue) or value.literal.enumeration is not type_: raise TypeError('Expected a literal of the declared Enumeration')
            value.literal._ensure_alive()
            return value
        if isinstance(value, ProfileObject):
            value._ensure_alive()
            if not value.classifier.conformsTo(type_): raise TypeError('Profile instance does not conform to the declared type')
            return value
        # A UML metaclass reference is different from a profile-defined Class.
        from .profile_filtering import referenced_metaclasses
        metaclasses = referenced_metaclasses(self._profile)
        if type_ in metaclasses:
            expected = type_.__registry__.get(type_.name)
            if expected is None: raise NativeNotImplemented('Metaclass reference requires a Python type adapter')
            if not isinstance(value, expected): raise TypeError('Expected an instance of the referenced metaclass')
            value._ensure_alive()
            return value
        raise TypeError('Expected a runtime profile-defined value, not an InstanceSpecification')

    def _normalize(self, prop, value, *, check_lower=True):
        upper, lower = prop.upperBound(), prop.lowerBound()
        many = upper > 1
        if many:
            if not isinstance(value, (tuple, list)): raise TypeError('Multivalued tag requires list or tuple')
            items = list(value)
        else: items = [] if value is None else [value]
        if any(v is None for v in items): raise TypeError('Null collection members are not allowed')
        items = [self._item(prop, v) for v in items]
        if prop.isUnique: items = list(dict.fromkeys(items))
        elif prop.association is not None and len(set(items)) != len(items):
            raise NativeNotImplemented('Repeated association links require explicit link identities')
        if len(items) > upper or check_lower and len(items) < lower: raise ValueError('Tag multiplicity violated')
        return tuple(items)

    def _default(self, prop):
        expression = prop.defaultValue
        if expression is None: return ()
        if expression.isNull(): value = None
        elif prop.type is not None and kind(prop,prop.type,'PrimitiveType') and prop.type.name not in ('Boolean','Integer','Real','String','UnlimitedNatural') and kind(prop,expression,'LiteralString') and expression.type is prop.type:
            value=PrimitiveValue(prop.type,expression.value)
        elif kind(prop, expression, 'InstanceValue'):
            value = expression.instance
            if value is not None and not kind(prop, value, 'EnumerationLiteral'):
                raise NativeNotImplemented('Default instance expression requires a runtime value adapter')
        else:
            queries = {'Boolean':'booleanValue','Integer':'integerValue','Real':'realValue','String':'stringValue','UnlimitedNatural':'unlimitedValue'}
            query = queries.get(None if prop.type is None else prop.type.name)
            if query is None: raise NativeNotImplemented('Default requires a runtime profile value adapter')
            value = getattr(expression, query)()
            if value is None:
                if expression.isComputable(): raise ValueError('Default does not denote the declared type')
                raise NativeNotImplemented('Default expression requires a language evaluator')
        return self._normalize(prop, [value] if prop.upperBound() > 1 and value is not None else ([] if prop.upperBound()>1 else value), check_lower=False)

    def get_value(self, key):
        prop = self._property(key)
        if prop.isDerived: raise NativeNotImplemented('Derived tagged value requires an evaluator')
        values = self._values[prop] if prop in self._values else self._default(prop)
        return tuple(values) if prop.upperBound() > 1 else (values[0] if values else None)

    @property
    def tagged_values(self):
        props = self._properties()
        if len({p.name for p in props}) != len(props): raise ValueError('Ambiguous tag names; use property identities')
        return MappingProxyType({p.name: self.get_value(p) for p in props})

    @property
    def values_by_property(self): return MappingProxyType({p: self.get_value(p) for p in self._properties()})

    def _update(self, values, *, initializing=False):
        if profile_evaluation.get(): raise ValueError('Cannot change tags during constraint evaluation')
        self._ensure_alive()
        if not hasattr(values, 'items'): raise TypeError('Expected property/value mapping')
        if not initializing and kind(self._classifier, self._classifier, 'DataType'): raise ValueError('DataType values are immutable after construction')
        staged = dict(self._values)
        resolved = set()
        for key, value in values.items():
            prop = self._property(key)
            if prop in resolved: raise ValueError('Property supplied twice')
            resolved.add(prop)
            if prop.isDerived or prop.isReadOnly and not initializing: raise ValueError('Property is read-only')
            staged[prop] = self._normalize(prop, value)
        self._commit(staged)

    def _commit(self, staged):
        # Plan navigable binary opposite changes before touching any runtime value.
        plans, pending = {self: staged}, [self]
        processed = set()
        while pending:
            source = pending.pop()
            if source in processed: continue
            processed.add(source)
            for prop in set(source._values) | set(plans[source]):
                association = prop.association
                if association is None: continue
                ends = list(association.memberEnd)
                if len(ends) != 2: raise NativeNotImplemented('Runtime profile associations must be binary')
                opposite = next((end for end in ends if end is not prop), None)
                if opposite is None: raise ValueError('Invalid association ends')
                before, after = source._values.get(prop, ()), plans[source].get(prop, ())
                for target in set(before) ^ set(after):
                    if not isinstance(target, ProfileObject): continue
                    if opposite not in target._properties(): continue  # Non-navigable association-owned end.
                    if kind(target.classifier, target.classifier, 'DataType'):
                        raise ValueError('Association updates cannot mutate a DataType value')
                    target_plan = plans.setdefault(target, dict(target._values))
                    values = list(target_plan.get(opposite, ()))
                    if target in after:
                        if source not in values: values.append(source)
                    else: values = [v for v in values if v is not source]
                    normalized = target._normalize(opposite, values if opposite.upperBound()>1 else (values[0] if len(values)==1 else None), check_lower=False)
                    if len(values) > opposite.upperBound(): raise ValueError('Opposite tag multiplicity violated')
                    if target in processed and normalized != target_plan.get(opposite, ()):
                        raise ValueError('Conflicting simultaneous association updates')
                    target_plan[opposite] = normalized
                    pending.append(target)
        for record, values in plans.items():
            record._check_composition(values)
        # All validation completed. Applying these plans cannot call user evaluators.
        for record, values in plans.items(): record._commit_local(values)

    def _check_composition(self, staged):
        owned = {}
        for prop, values in staged.items():
            if not prop.isComposite: continue
            if not kind(prop, prop.type, 'Class') or defining_profile(prop.type) is None:
                raise ValueError('Composite profile properties require a profile-defined Class')
            for value in values:
                if not isinstance(value, ProfileObject): raise TypeError('Composite tags require runtime profile instances')
                if value in owned: raise ValueError('Composite instance occurs in multiple properties')
                owned[value] = prop
                old = value._composite_owner
                if old is not None and old[0] is not self: raise ValueError('Profile instance already has a composite owner')
                ancestor = self
                while ancestor is not None:
                    if ancestor is value: raise ValueError('Profile composition cycle')
                    ancestor = None if ancestor._composite_owner is None else ancestor._composite_owner[0]
        return owned

    def _commit_local(self, staged):
        owned = {v:p for p, values in staged.items() if p.isComposite for v in values}
        old_children = {v for p, values in self._values.items() if p.isComposite for v in values}
        for child in old_children - set(owned):
            child._package = self.package
            child._composite_owner = None
        self._values = staged
        for child, prop in owned.items(): child._composite_owner = (self, prop)
        if self in _records:
            self._register()
            for child in old_children - set(owned): child._register()

    def set_value(self, key, value): self._update({key:value}); return self
    def set_values(self, values): self._update(values); return self

    def unset_value(self, key):
        if profile_evaluation.get(): raise ValueError('Cannot change tags during constraint evaluation')
        prop = self._property(key)
        if prop.isDerived or prop.isReadOnly or kind(self._classifier, self._classifier, 'DataType'): raise ValueError('Property is read-only')
        if len(self._default(prop)) < prop.lowerBound(): raise ValueError('Required tag has no default')
        staged = dict(self._values); staged.pop(prop, None)
        self._commit(staged)
        return self

    def _validate_values(self):
        issues = []
        self._ensure_alive()
        from .stereotypes import available_profiles
        if self.package is None or self._profile not in available_profiles(self.package):
            issues.append(('stereotype application','Profile.type_available'))
        props = self._properties()
        for obsolete in set(self._values)-set(props): issues.append(('stereotype application','Profile.obsolete_tag'))
        for prop in props:
            key = 'Profile.tag:'+ (prop.name or '<unnamed>')
            try:
                value = self.get_value(prop)
                normalized=self._normalize(prop, value)
                if any(isinstance(v,PrimitiveValue) and not v.has_semantics for v in normalized):
                    issues.append(('unsupported stereotype application',key))
            except NativeNotImplemented: issues.append(('unsupported stereotype application',key))
            except (ValueError, TypeError): issues.append(('stereotype application',key))
        for classifier in [self._classifier] + self._classifier.allParents():
            for constraint in classifier.ownedRule:
                identifier = 'Profile.constraint:'+ (constraint.qualifiedName or constraint.name or '<unnamed>')
                try:
                    predicate = _constraint_adapters.get(constraint)
                    if predicate is not None:
                        token = profile_evaluation.set(True)
                        try: result = predicate(self)
                        finally: profile_evaluation.reset(token)
                    elif constraint.specification is not None and constraint.specification.isComputable(): result = constraint.specification.booleanValue()
                    else: raise NativeNotImplemented('User constraint requires a registered evaluator')
                    if type(result) is not bool: raise ValueError('Constraint evaluator must return Boolean')
                    if not result: issues.append(('stereotype application',identifier))
                except NativeNotImplemented: issues.append(('unsupported stereotype application',identifier))
                except Exception: issues.append(('invalid stereotype application',identifier))
        return issues

    def validate(self): return self._validate_values()

    def delete(self):
        if profile_evaluation.get(): raise ValueError('Cannot delete values during constraint evaluation')
        if self._deleted: return ()
        doomed = _runtime_closure({self})
        _delete_records(doomed)
        return tuple(doomed)


def _runtime_closure(initial):
    doomed, pending = set(), list(initial)
    while pending:
        value = pending.pop()
        if value in doomed: continue
        doomed.add(value)
        pending.extend(v for values in value._values.values() for v in values
                       if isinstance(v, ProfileObject) and v._composite_owner is not None and v._composite_owner[0] is value)
    return doomed


def _delete_records(doomed, model_doomed=()):
    model_doomed = set(model_doomed)
    for record in list(_records):
        for prop, values in list(record._values.items()):
            kept = tuple(v for v in values if v not in doomed and v not in model_doomed
                         and not (isinstance(v, EnumValue) and v.literal in model_doomed)
                         and not (isinstance(v,PrimitiveValue) and v.classifier in model_doomed))
            if prop in model_doomed: kept = ()
            if record in doomed: kept = ()
            if kept != values or prop in model_doomed:
                for value in values:
                    if isinstance(value, ProfileObject) and value._composite_owner == (record, prop) and value not in kept:
                        value._package = record.package
                        value._composite_owner = None
                if prop in model_doomed: record._values.pop(prop, None)
                else: record._values[prop] = kept
        if record in doomed:
            if hasattr(record, 'detach'): record.detach()
            record._values.clear()
            record._deleted = True
            if record._registry_package is not None: getattr(record._registry_package, '_profile_instances', set()).discard(record)
            _records.discard(record)


def plan_profile_cleanup(model_doomed=(), runtime_doomed=()):
    from .stereotypes import available_profiles
    model_doomed = set(model_doomed)
    initial = set(runtime_doomed)
    for record in list(_records):
        if record.classifier in model_doomed or record._profile in model_doomed or getattr(record, 'element', None) in model_doomed or record.package in model_doomed:
            initial.add(record)
        elif record.package is not None and record._profile not in available_profiles(record.package): initial.add(record)
    return _runtime_closure(initial)


def cleanup_profile_values(model_doomed=(), runtime_doomed=()):
    _delete_records(plan_profile_cleanup(model_doomed, runtime_doomed), model_doomed)
    for constraint in model_doomed: _constraint_adapters.pop(constraint, None)
