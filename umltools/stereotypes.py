"""Runtime stereotype-to-element links (UML 12.3.3.3, .4 and .6).

Applications are runtime objects, distinct from the Stereotype metaclass which
describes their classifier. Their mutually exclusive base slots are read-only.
"""
from types import MappingProxyType
from .native import kind, instances, NativeNotImplemented, check
from .native.constraints_remaining import base_properties
from .profile_values import ProfileObject, containing_package, cleanup_profile_values, _records
from .evaluation_context import profile_evaluation


def _definition_issues(stereotype):
    if stereotype.__semantic_version__=='2.4.1':
        from .semantics241_profiles import definition_issues
        return definition_issues(stereotype)
    return [identifier for identifier in ('Stereotype.base_property_upper_bound',
        'Stereotype.base_property_multiplicity_single_extension',
        'Stereotype.base_property_multiplicity_multiple_extension') if not check(stereotype,identifier)]


def available_profiles(element):
    direct, seen = [], set()
    current = element
    while current is not None:
        if current in seen: raise ValueError('Cyclic ownership')
        seen.add(current)
        if kind(element, current, 'Package'):
            direct.extend(a.appliedProfile for a in current.profileApplication if a.appliedProfile is not None)
        current = current.owner
    result, pending = set(), direct
    while pending:
        profile = pending.pop()
        if profile in result: continue
        result.add(profile)
        pending.extend(p for p in profile.packagedElement if kind(element, p, 'Profile'))
        pending.extend(i.importedPackage for i in profile.packageImport if kind(element, i.importedPackage, 'Profile'))
        from .profile_values import defining_profile
        pending.extend(p for i in profile.elementImport if kind(element, i.importedElement, 'Stereotype')
                       for p in [defining_profile(i.importedElement)] if p is not None)
    return result


def _metaclass_type(element, property_):
    metaclass = property_.type
    if metaclass is None: raise ValueError('Base property has no metaclass')
    result = element.__registry__.get(metaclass.name)
    if result is None or not hasattr(result, '__spec__'):
        raise NativeNotImplemented('A non-UML extension needs a metaclass-to-Python-type adapter')
    return result


def _families(stereotype):
    return {s for s in [stereotype] + stereotype.allParents() if kind(stereotype, s, 'Stereotype') and base_properties(s)}


def _conforms_to_base(element, prop):
    if kind(element, element, 'InstanceSpecification') and any(c.conformsTo(prop.type) for c in element.classifier): return True
    return isinstance(element, _metaclass_type(element, prop))


def _modeled_applications(element):
    result = []
    for candidate in instances(element, 'InstanceSpecification'):
        for stereotype in candidate._items(candidate.classifier):
            if not kind(element, stereotype, 'Stereotype'): continue
            props = base_properties(stereotype)
            if any(slot.definingFeature in props and any(kind(element, v, 'InstanceValue') and v.instance is element for v in slot.value) for slot in candidate.slot):
                result.append((candidate, stereotype))
    return result


def _present_stereotypes(element):
    classifiers = [app.stereotype for app in applications(element)] + [s for _, s in _modeled_applications(element)]
    return {s for stereotype in classifiers for s in [stereotype] + stereotype.allParents()}


def applications(element):
    from .native import require_version
    require_version(element)
    return tuple(getattr(element, '_stereotype_applications', {}).values())


def _available_stereotypes(element):
    from .profile_filtering import applied_roots, visible_stereotypes
    return {s for application in applied_roots(element) for s in visible_stereotypes(application.appliedProfile)}


def apply_profile(package, profile, *, create_required=True, is_strict=None):
    if is_strict is not None and type(is_strict) is not bool: raise TypeError('is_strict must be Boolean')
    if not kind(package, package, 'Package') or not kind(package, profile, 'Profile'):
        raise TypeError('Expected a Package and a Profile')
    package._ensure_alive(); profile._ensure_alive()
    existing = next((a for a in package.profileApplication if a.appliedProfile is profile), None)
    application = existing or package.__registry__['ProfileApplication'](appliedProfile=profile)
    previous_strict = application.isStrict
    if is_strict is not None:
        application.isStrict = is_strict
    created = []
    if existing is None: package.profileApplication.append(application)
    try:
        from .profile_filtering import validate_strict_profiles
        if validate_strict_profiles(application): raise ValueError('Conflicting strict profile filters')
        if create_required:
            for element in [package] + package.allOwnedElements():
                stereotypes = _available_stereotypes(element)
                for stereotype in sorted(stereotypes, key=lambda s: s.qualifiedName or s.name or ''):
                    present = _present_stereotypes(element)
                    if stereotype in present: continue
                    for prop in base_properties(stereotype):
                        if not prop.association.isRequired or not _conforms_to_base(element, prop): continue
                        candidates = ([stereotype] if not stereotype.isAbstract else
                                      [s for s in stereotypes if not s.isAbstract and stereotype in s.allParents()])
                        if len(candidates) != 1:
                            raise ValueError('A required abstract stereotype needs one unambiguous concrete subtype')
                        concrete = candidates[0]
                        props = [p for p in base_properties(concrete) if p is prop or prop in p.redefinedProperty]
                        if len(props) != 1: raise ValueError('Required base property has an ambiguous redefinition')
                        created.append(apply_stereotype(element, concrete, base_property=props[0]))
    except Exception:
        for app in created: app.delete()
        if existing is None:
            package.profileApplication.remove(application)
            application.delete()
        else: application.isStrict = previous_strict
        raise
    return application


def unapply_profile(package, profile):
    if not kind(package, package, 'Package') or not kind(package, profile, 'Profile'):
        raise TypeError('Expected a Package and a Profile')
    package._ensure_alive();profile._ensure_alive()
    if package.__semantic_version__=='2.4.1':
        from .profile_filtering import applied_roots,profile_closure
        if any(a.appliedProfile is profile for a in package.profileApplication) and any(a.appliedProfile is not profile and profile in profile_closure(a.appliedProfile) for a in applied_roots(package)):
            raise ValueError('Remove applied dependent profiles first (UML 2.4.1 ProfileApplication)')
    elements = [package] + package.allOwnedElements()
    modeled = {instance for element in elements for instance, _ in _modeled_applications(element)}
    modeled.update(e for e in elements if kind(package, e, 'InstanceSpecification'))
    for application in list(package.profileApplication):
        if application.appliedProfile is profile: application.delete()
    elements = [element for element in elements if not element.is_deleted]
    for element in elements:
        available = available_profiles(element)
        for app in applications(element):
            if app.stereotype.profile not in available: app.detach()
    for instance in modeled:
        if instance.is_deleted: continue
        available = available_profiles(instance)
        if instance.owner is None:
            for slot in instance.slot:
                for value in slot.value:
                    if kind(instance, value, 'InstanceValue') and value.instance is not None:
                        available.update(available_profiles(value.instance))
        def defining_profile(classifier):
            current, seen = classifier.owner, set()
            while current is not None:
                if current in seen: raise ValueError('Cyclic profile ownership')
                seen.add(current)
                if kind(instance, current, 'Profile'): return current
                current = current.owner
            return None
        remaining = [c for c in instance.classifier if defining_profile(c) is None or defining_profile(c) in available]
        if len(remaining) == len(instance.classifier): continue
        if not remaining:
            instance.delete()
            continue
        instance.classifier = remaining
        for slot in list(instance.slot):
            if slot.definingFeature is None or (defining_profile(slot.definingFeature) is not None and defining_profile(slot.definingFeature) not in available):
                slot.delete()
    cleanup_profile_values()


class StereotypeApplication(ProfileObject):
    def __init__(self, stereotype, element, *, base_property=None, values=None):
        if not kind(stereotype, stereotype, 'Stereotype'): raise TypeError('Expected a Stereotype')
        self._stereotype = stereotype
        self._element = None
        self._base_property = None
        self._init_values(stereotype, containing_package(element))
        self.rebind(element, base_property=base_property)
        try:
            self._update(values or {}, initializing=True)
            self._register()
        except Exception:
            self._commit({})
            self.detach()
            raise

    @property
    def stereotype(self): return self._stereotype

    @property
    def element(self): return self._element

    @property
    def base_slots(self):
        return MappingProxyType({p: self._element if p is self._base_property else None for p in base_properties(self.stereotype)})

    def rebind(self, element, *, base_property=None):
        if profile_evaluation.get(): raise ValueError('Cannot rebind during constraint evaluation')
        self._ensure_alive()
        stereotype = self.stereotype
        if not hasattr(element, '__spec__'): raise TypeError('Expected a UML model element')
        stereotype._ensure_alive()
        element._ensure_alive()
        if stereotype.isAbstract: raise ValueError('An abstract stereotype cannot be instantiated')
        if stereotype.profile not in available_profiles(element) or stereotype not in _available_stereotypes(element):
            raise ValueError('Apply the containing profile to this element\'s package first')
        if stereotype.visibility is not None and stereotype.visibility.value != 'public':
            raise ValueError('Only public stereotypes of applied profiles are available')
        props = base_properties(stereotype)
        issues=_definition_issues(stereotype)
        if issues:raise ValueError('Invalid definition: '+', '.join(issues))
        candidates = [p for p in props if _conforms_to_base(element, p)]
        if isinstance(base_property, str):
            named = [p for p in props if p.name == base_property]
            if len(named) != 1: raise ValueError('Base property name must identify one property')
            base_property = named[0]
        if base_property is None:
            if len(candidates) != 1: raise ValueError('Select exactly one compatible base property')
            base_property = candidates[0]
        if base_property not in candidates: raise ValueError('The element does not conform to the selected metaclass')
        families = _families(stereotype)
        for app in applications(element):
            if app is not self and families & _families(app.stereotype):
                raise ValueError('A stereotype or its subtypes cannot be applied twice to one element')
        if any(families & _families(s) for _, s in _modeled_applications(element)):
            raise ValueError('A modeled stereotype application already exists for this element')
        # Check everything before removing the old link, so a failed rebind is atomic.
        old = self._element
        if old is not None:
            old._stereotype_applications = {s: a for s, a in getattr(old, '_stereotype_applications', {}).items() if a is not self}
        self._element, self._base_property = element, base_property
        element._stereotype_applications = {**getattr(element, '_stereotype_applications', {}), stereotype: self}
        self._package = containing_package(element)
        if self in _records: self._register()
        return self

    def detach(self):
        if profile_evaluation.get(): raise ValueError('Cannot detach during constraint evaluation')
        if self._element is not None:
            element = self._element
            element._stereotype_applications = {s: a for s, a in getattr(element, '_stereotype_applications', {}).items() if a is not self}
        self._element = None
        self._base_property = None

    def validate(self):
        self._ensure_alive()
        issues = []
        if self.element is None: return [('stereotype application', 'Stereotype.base_instance')]
        slots = self.base_slots
        if sum(value is not None for value in slots.values()) != 1:
            issues.append(('stereotype application', 'Stereotype.base_instance'))
        elif not _conforms_to_base(self.element, self._base_property):
            issues.append(('stereotype application', 'Stereotype.base_instance'))
        if self.stereotype.profile not in available_profiles(self.element):
            issues.append(('stereotype application', 'Stereotype.profile_available'))
        if self.stereotype.visibility is not None and self.stereotype.visibility.value != 'public':
            issues.append(('stereotype application', 'Stereotype.profile_available'))
        if self.stereotype.isAbstract:
            issues.append(('stereotype application', 'Stereotype.abstract_instance'))
        if any(app is not self and _families(self.stereotype) & _families(app.stereotype) for app in applications(self.element)):
            issues.append(('stereotype application', 'Stereotype.duplicate_application'))
        try:issues.extend(('stereotype application',identifier) for identifier in _definition_issues(self.stereotype))
        except NativeNotImplemented:issues.append(('unsupported stereotype application','prose:Stereotype.base_link_bounds'))
        issues.extend(self._validate_values())
        return issues


def apply_stereotype(element, stereotype, *, base_property=None, values=None):
    return StereotypeApplication(stereotype, element, base_property=base_property, values=values)


def _validate_instance_applications(instance):
    """Validate applications explicitly modeled as InstanceSpecification/Slot."""
    result = []
    for stereotype in instance._items(instance.classifier):
        if not kind(instance, stereotype, 'Stereotype'): continue
        props = base_properties(stereotype)
        populated = []
        for prop in props:
            slots = [slot for slot in instance.slot if slot.definingFeature is prop]
            values = [value for slot in slots for value in slot.value if not kind(instance, value, 'LiteralNull')]
            if len(slots) > 1 or len(values) > 1:
                identifier='prose:Stereotype.base_link_upper_bound' if instance.__semantic_version__=='2.4.1' else 'Stereotype.base_property_upper_bound'
                result.append(('stereotype application',identifier))
            for value in values:
                if not kind(instance, value, 'InstanceValue') or value.instance is None:
                    result.append(('stereotype application', 'Stereotype.base_instance'))
                    continue
                target = value.instance
                if not any(c.conformsTo(prop.type) for c in target.classifier):
                    result.append(('stereotype application', 'Stereotype.base_instance'))
                if stereotype.profile not in available_profiles(target):
                    result.append(('stereotype application', 'Stereotype.profile_available'))
                populated.append(target)
        if len(populated) != 1:
            rule = ('Stereotype.base_property_multiplicity_multiple_extension' if len(props) > 1
                    else 'Stereotype.base_property_multiplicity_single_extension')
            if instance.__semantic_version__=='2.4.1':rule='prose:Stereotype.exclusive_base_instance'
            result.append(('stereotype application', rule))
        else:
            target = populated[0]
            if any(other is not instance and _families(stereotype) & _families(s) for other, s in _modeled_applications(target)) or any(_families(stereotype) & _families(app.stereotype) for app in applications(target)):
                result.append(('stereotype application', 'Stereotype.duplicate_application'))
        if stereotype.isAbstract:
            result.append(('stereotype application', 'Stereotype.abstract_instance'))
    return result


def validate_applications(element):
    result = [issue for app in applications(element) for issue in app.validate()]
    if kind(element, element, 'Package'):
        result.extend(issue for value in getattr(element, '_profile_instances', ())
                      if not isinstance(value, StereotypeApplication) for issue in value.validate())
    from .profile_filtering import validate_strict_profiles
    result.extend(validate_strict_profiles(element))
    if kind(element, element, 'InstanceSpecification'):
        result.extend(_validate_instance_applications(element))
    available = _available_stereotypes(element)
    if not available: return list(dict.fromkeys(result))
    present = _present_stereotypes(element)
    for stereotype in available:
        for p in base_properties(stereotype):
            if p.association.isRequired and _conforms_to_base(element, p) and stereotype not in present:
                result.append(('stereotype application', 'Stereotype.required_extension'))
    return list(dict.fromkeys(result))
