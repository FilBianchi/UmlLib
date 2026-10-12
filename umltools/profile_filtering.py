"""Strict profile availability is a view, never deletion of existing UML objects."""
from .native import kind, NativeNotImplemented


def profile_closure(profile):
    result, pending = set(), [profile]
    while pending:
        current = pending.pop()
        if current in result: continue
        current._ensure_alive()
        result.add(current)
        pending.extend(i.importedPackage for i in current.packageImport if kind(profile, i.importedPackage, 'Profile'))
        from .profile_values import defining_profile
        pending.extend(p for i in current.elementImport if kind(profile, i.importedElement, 'Stereotype')
                       for p in [defining_profile(i.importedElement)] if p is not None)
    return result


def referenced_metaclasses(profile):
    if profile is None: return set()
    closure = profile_closure(profile)
    explicit = {i.importedElement for p in closure for i in p.metaclassReference if i.importedElement is not None}
    if explicit: return explicit
    packages = [i.importedPackage for p in closure for i in p.metamodelReference if i.importedPackage is not None]
    result, seen = set(), set()
    while packages:
        package = packages.pop()
        if package in seen: continue
        seen.add(package)
        for member in package.member:
            if kind(profile, member, 'Package'): packages.append(member)
            elif kind(profile, member, 'Class'): result.add(member)
    return result


def visible_stereotypes(profile):
    result, seen, pending = set(), set(), [profile]
    while pending:
        package = pending.pop()
        if package in seen: continue
        seen.add(package)
        for member in package.packagedElement:
            if member.visibility is not None and member.visibility.value != 'public': continue
            if kind(profile, member, 'Stereotype'): result.add(member)
            elif kind(profile, member, 'Package'): pending.append(member)
        for import_ in package.packageImport:
            if import_.visibility.value == 'public' and import_.importedPackage is not None: pending.append(import_.importedPackage)
        for import_ in package.elementImport:
            member = import_.importedElement
            if import_.visibility.value == 'public' and kind(profile, member, 'Stereotype') and (member.visibility is None or member.visibility.value == 'public'): result.add(member)
    return result


def applied_roots(element, *, strict_only=False):
    applications, current = [], element
    while current is not None:
        if kind(element, current, 'Package'):
            applications.extend(a for a in current.profileApplication if a.appliedProfile is not None and (not strict_only or a.isStrict))
        current = current.owner
    return applications


def available_metaclasses(profile):
    from .native.constraints_remaining import base_properties
    referenced = referenced_metaclasses(profile)
    result = set()
    for metaclass in referenced:
        if metaclass.name not in profile.__registry__ or not hasattr(profile.__registry__[metaclass.name], '__spec__'):
            raise NativeNotImplemented('Profile filter requires a metaclass adapter: '+str(metaclass.name))
        result.add(metaclass.name)
    for stereotype in visible_stereotypes(profile):
        for prop in base_properties(stereotype):
            if prop.type is None or prop.type.name not in profile.__registry__: raise NativeNotImplemented('Unknown extended metaclass')
            extended = profile.__registry__[prop.type.name]
            result.update(name for name, cls in profile.__registry__.items()
                          if hasattr(cls, '__spec__') and issubclass(cls, extended))
    return frozenset(result)


def is_metaclass_available(package, metaclass):
    package._ensure_alive()
    name = metaclass if isinstance(metaclass, str) else metaclass.__spec__.name
    if name not in package.__registry__ or not hasattr(package.__registry__[name], '__spec__'): raise ValueError('Unknown UML metaclass')
    return all(name in available_metaclasses(a.appliedProfile) for a in applied_roots(package, strict_only=True))


def is_element_available(element):
    element._ensure_alive()
    if not is_metaclass_available(element, element.__spec__.name): return False
    if kind(element, element, 'Relationship'):
        return all(is_metaclass_available(e, e.__spec__.name) for e in element.relatedElement)
    return True


def create_profiled_element(package, metaclass, **values):
    if not kind(package, package, 'Package'): raise TypeError('Expected Package')
    name = metaclass if isinstance(metaclass, str) else metaclass.__spec__.name
    if not is_metaclass_available(package, name): raise ValueError('Metaclass is hidden by a strict profile')
    # Creation returns an unowned object so the caller chooses the correct UML end.
    from .model_session import current_session
    token = current_session.set(package._extent)
    try: return package.__registry__[name](**values)
    finally: current_session.reset(token)


def validate_strict_profiles(element):
    issues = []
    if kind(element, element, 'ProfileApplication') and element.isStrict:
        if element.applyingPackage is None or element.appliedProfile is None: return [('stereotype application','Profile.strict_context')]
        sets = [available_metaclasses(a.appliedProfile) for a in applied_roots(element.applyingPackage, strict_only=True)]
        if len(sets) > 1 and not set.intersection(*(set(s) for s in sets)):
            issues.append(('stereotype application','Profile.strict_conflict'))
    # Profile-defined Types are not substitute types in the underlying UML model.
    from .profile_values import defining_profile
    candidates = []
    if kind(element, element, 'TypedElement') and element.type is not None: candidates.append(element.type)
    if kind(element, element, 'InstanceSpecification'):
        # Legacy explicit application encodings retain their separate base-link audit.
        candidates.extend(c for c in element._items(element.classifier) if not kind(element, c, 'Stereotype'))
    if kind(element, element, 'Generalization'): candidates.extend(c for c in (element.general, element.specific) if c is not None)
    current, inside_profile = element, False
    while current is not None:
        inside_profile |= kind(element, current, 'Profile')
        current = current.owner
    if not inside_profile:
        if any(defining_profile(c) is not None for c in candidates): issues.append(('stereotype application','Profile.type_in_model'))
    return issues
