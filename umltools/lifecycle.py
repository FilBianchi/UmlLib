"""Explicit model deletion, independent of Python garbage collection."""


class DeletedElementError(RuntimeError):
    """A logically deleted element cannot be used as a model element."""


class DeletionRestrictedError(ValueError):
    """Deletion was refused without changing the model."""


def delete(element, *, cascade=True, on_references='detach'):
    """Delete an element and its composite descendants atomically.

    ``detach`` clears surviving references; required references then fail validation.
    ``restrict`` refuses external references other than the composite parent link.
    References in other live sessions are included in cleanup. Python variables and
    application-owned metadata are not UML references and are not rewritten.
    """
    from . import UmlElement, _mutation
    from .stereotypes import applications, available_profiles
    from .native import kind
    from .evaluation_context import profile_evaluation
    if profile_evaluation.get(): raise ValueError('Cannot delete elements during constraint evaluation')
    if not isinstance(element, UmlElement): raise TypeError('Expected a UML model element')
    if on_references not in ('detach', 'restrict'): raise ValueError('Unknown reference policy')
    if type(cascade) is not bool: raise TypeError('cascade must be Boolean')
    if element.is_deleted: return ()
    if _mutation.get() is not None: raise RuntimeError('Deletion cannot run inside another model mutation')
    live = [e for e in UmlElement.__instances__ if not e.is_deleted]
    modeled_bases = {}
    for candidate in live:
        classifiers = candidate._items(candidate._values.get('classifier'))
        if not any(kind(candidate, c, 'Stereotype') for c in classifiers): continue
        for slot in candidate._items(candidate._values.get('slot')):
            feature = slot._values.get('definingFeature')
            if feature is None or not kind(candidate, feature._values.get('association'), 'Extension'): continue
            for value in slot._items(slot._values.get('value')):
                if not kind(candidate, value, 'InstanceValue'): continue
                base = value._values.get('instance')
                if base is not None: modeled_bases.setdefault(base, set()).add(candidate)
    doomed, pending = set(), [element]
    while pending:
        current = pending.pop()
        if current in doomed: continue
        children = [child for name, prop in current.properties().items()
                    if prop.flags.get('aggregation') == 'composite' and prop.flags.get('isDerived') != 'true'
                    for child in current._items(current._values.get(name)) if isinstance(child, UmlElement)]
        if children and not cascade:
            raise DeletionRestrictedError('The element owns composite children; use cascade=True')
        doomed.add(current)
        pending.extend(children)
        # Modeled stereotype instances cannot retain an application to a deleted base.
        pending.extend(modeled_bases.get(current, ()))
        for candidate in live:
            if candidate.__spec__.name == 'ProfileApplication' and candidate._values.get('appliedProfile') is current:
                pending.append(candidate)
            classifiers = candidate._items(candidate._values.get('classifier'))
            if classifiers and all(c in doomed for c in classifiers) and any(c.__spec__.name == 'Stereotype' for c in classifiers):
                pending.append(candidate)
    if on_references == 'restrict':
        from .profile_values import _records, EnumValue, plan_profile_cleanup
        internal_values = plan_profile_cleanup(doomed)
        for record in list(_records):
            if record in internal_values: continue
            for prop, values in record._values.items():
                if prop in doomed or any(v in doomed or isinstance(v, EnumValue) and v.literal in doomed for v in values):
                    raise DeletionRestrictedError('A runtime tagged value prevents deletion')
        for survivor in live:
            if survivor in doomed: continue
            for name, prop in survivor.properties().items():
                if prop.flags.get('isDerived') == 'true': continue
                targets = [v for v in survivor._items(survivor._values.get(name)) if isinstance(v, UmlElement) and v in doomed]
                if targets and prop.flags.get('aggregation') != 'composite':
                    raise DeletionRestrictedError(f'External reference {prop.id} prevents deletion')
            if any(app.stereotype in doomed or app._base_property in doomed for app in applications(survivor)):
                raise DeletionRestrictedError('A runtime stereotype application prevents deletion')
    transaction = {'snapshots': {}, 'active': set()}
    application_state = {app: (app._element, app._base_property) for source in live for app in applications(source)}
    application_maps = {source: dict(source._stereotype_applications) for source in live if hasattr(source, '_stereotype_applications')}
    token = _mutation.set(transaction)
    try:
        for source in live:
            for name, prop in source.properties().items():
                if prop.flags.get('isDerived') == 'true': continue
                values = source._items(source._values.get(name))
                kept = [v for v in values if not (isinstance(v, UmlElement) and (source in doomed or v in doomed))]
                if kept != values:
                    setattr(source, name, kept if prop.upper is None or prop.upper > 1 else (kept[0] if kept else None))
        # Compute all potentially failing queries before changing application metadata.
        detach = []
        for source in live:
            for app in applications(source):
                if source in doomed or app.stereotype in doomed or app._base_property in doomed:
                    detach.append(app)
                else:
                    current, affected = source, False
                    while current is not None:
                        affected |= id(current) in transaction['snapshots']
                        current = current._container
                    if affected and app.stereotype.profile not in available_profiles(source): detach.append(app)
        from .profile_values import plan_profile_cleanup
        profile_doomed = plan_profile_cleanup(doomed, detach)
        for app in detach: app.detach()
    except Exception:
        UmlElement._rollback(transaction)
        for app, (base, prop) in application_state.items():
            app._element, app._base_property = base, prop
        for source, mapping in application_maps.items(): object.__setattr__(source, '_stereotype_applications', mapping)
        raise
    finally:
        _mutation.reset(token)
    from .expression_semantics import _facts, _collection_types
    for expression, facts in list(_facts.items()):
        if expression in doomed or any(isinstance(v, UmlElement) and v in doomed for v in facts.references or ()):
            _facts.pop(expression, None)
    for item in doomed: _collection_types.discard(item)
    for source in live:
        # Discard official adapter mappings that reference a tombstone.
        for field in ('_gate_endpoint_bindings', '_extra_global_fragments', '_occurrence_gate_mappings'):
            mapping = getattr(source, field, None)
            if mapping is None: continue
            kept = {key: value for key, value in mapping.items()
                    if key not in doomed and all(not isinstance(v, UmlElement) or v not in doomed
                                                for v in (value if isinstance(value, tuple) else (value,)))}
            object.__setattr__(source, field, {} if source in doomed else kept)
    for item in doomed:
        object.__setattr__(item, '_deleted', True)
        item.__instances__.discard(item)
        if item._extent is not None: item._extent.elements.discard(item)
        object.__setattr__(item, '_extent', None)
    from .profile_values import _delete_records, _constraint_adapters
    _delete_records(profile_doomed, doomed)
    for item in doomed: _constraint_adapters.pop(item, None)
    return tuple(doomed)
