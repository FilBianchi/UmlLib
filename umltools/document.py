"""Public lifecycle operations for an XMI document's isolated model extent."""
from importlib import import_module
from uuid import uuid4
import copy


def writable(prop):
    return prop.flags.get('isDerived') != 'true' and prop.flags.get('isReadOnly') != 'true'


class DocumentEditing:
    @classmethod
    def new(cls, name='Model', *, uri='memory:/model.xmi', semantic_version=None):
        from . import ModelSession
        from .versions import SEMANTIC_VERSION
        if not isinstance(uri,str) or not uri or '#' in uri:
            raise ValueError('Document URI must be a nonempty resource URI without a fragment')
        if semantic_version not in (None, SEMANTIC_VERSION):
            if __package__ == 'umltools' and semantic_version == '2.4.1':
                from .version_backend import backend_241
                return backend_241().xmi.XmiDocument.new(name, uri=uri)
            raise ValueError('New documents require the selected UML backend')
        document = cls(uri, ModelSession())
        document.create('Model', name=name)
        return document

    def classifiers(self):
        """Concrete public metaclasses belonging to this document's backend."""
        facade = import_module('Uml241' if self.semantic_version == '2.4.1' else 'Uml251')
        result = {}
        for name, raw in facade.Model.__registry__.items():
            if not isinstance(raw, type) or not hasattr(raw, '__spec__') or raw.__spec__.abstract:
                continue
            cls = getattr(facade, name, raw)
            if not isinstance(cls, type):
                cls = facade.StateMachines.StateMachine if name == 'StateMachine' else raw
            result[name] = cls
        return result

    def _member(self, element):
        from . import UmlElement
        if not isinstance(element, UmlElement):
            raise TypeError('Expected a UML element from this backend')
        element._ensure_alive()
        if element._extent is not self.session:
            raise ValueError('Element does not belong to this document session')

    def containment_features(self, owner):
        self._member(owner)
        return {name: prop for name, prop in owner.properties().items()
                if writable(prop) and prop.flags.get('aggregation') == 'composite'}

    def compatible_classes(self, owner=None, feature=None):
        classes = self.classifiers()
        if owner is None:
            if feature is not None: raise ValueError('A feature requires an owner')
            return tuple(sorted(classes))
        self._member(owner)
        prop = self.containment_features(owner).get(feature)
        if prop is None: raise ValueError('Expected a writable composite property')
        target = owner.__registry__.get(prop.type)
        return tuple(sorted(name for name, cls in classes.items() if isinstance(target, type) and issubclass(cls, target)))

    def create(self, class_name, *, owner=None, feature=None, **values):
        from . import UmlElement, _mutation
        if _mutation.get() is not None: raise RuntimeError('Creation cannot nest inside another mutation')
        if class_name not in self.compatible_classes(owner, feature):
            raise TypeError('Incompatible or abstract metaclass: '+class_name)
        cls = self.classifiers()[class_name]
        for value in values.values():
            for target in UmlElement._items(value):
                if isinstance(target,UmlElement): self._member(target)
        if owner is not None:
            prop = owner.properties()[feature]
            current = getattr(owner, feature)
            if prop.upper is not None and prop.upper <= 1 and current is not None:
                raise ValueError('Composite property is occupied')
        before=set(self.session.elements)
        transaction={'snapshots':{},'active':set()}
        token=_mutation.set(transaction)
        try:
            from .model_session import current_session
            if current_session.get() is self.session:
                element = cls(**values)
            else:
                with self.session:
                    element = cls(**values)
            if owner is not None:
                setattr(owner, feature, list(current)+[element] if prop.upper is None or prop.upper > 1 else element)
                element._xmi_uri = getattr(owner, '_xmi_uri', None) or self.uri
        except Exception:
            UmlElement._rollback(transaction)
            # Do not cascade-delete preexisting objects supplied as composites.
            for created in self.session.elements-before:
                created.__instances__.discard(created)
                object.__setattr__(created,'_deleted',True)
                object.__setattr__(created,'_extent',None)
            self.session.elements.intersection_update(before)
            raise
        finally:
            _mutation.reset(token)
        self.synchronize()
        return element

    def set_value(self, element, feature, value):
        self._member(element)
        prop = element.properties().get(feature)
        if prop is None or not writable(prop):
            raise ValueError('Expected a writable stored UML property')
        # References managed here must belong to the same extent. Legacy setters
        # retain their existing permissive cross-session contract.
        from . import UmlElement
        for target in element._items(value):
            if isinstance(target, UmlElement): self._member(target)
        setattr(element, feature, value)
        self.synchronize()

    def move(self, element, *, owner=None, feature=None):
        """Atomically detach and attach, restoring both owners on failure."""
        from . import _mutation, UmlElement
        self._member(element)
        if _mutation.get() is not None: raise RuntimeError('Move cannot nest inside another mutation')
        if owner is not None:
            self._member(owner)
            if element.__spec__.name not in self.compatible_classes(owner, feature):
                raise TypeError('Incompatible destination')
            prop = owner.properties()[feature]
            current = getattr(owner, feature)
            if prop.upper is not None and prop.upper <= 1 and current not in (None, element):
                raise ValueError('Destination is occupied')
        elif feature is not None:
            raise ValueError('A feature requires an owner')
        previous_owner = element.owner
        transaction = {'snapshots': {}, 'active': set()}
        token = _mutation.set(transaction)
        try:
            if previous_owner is not None:
                links = [(name, prop, getattr(previous_owner, name)) for name, prop in self.containment_features(previous_owner).items()
                         if element in previous_owner._items(getattr(previous_owner, name))]
                for name, prop, value in links:
                    setattr(previous_owner, name, [v for v in value if v is not element] if prop.upper is None or prop.upper > 1 else None)
                if element.owner is not None:
                    from . import UnsupportedSemanticsError
                    raise UnsupportedSemanticsError('Containment has no writable detachment path')
            if owner is not None:
                current = getattr(owner, feature)
                setattr(owner, feature, list(current)+[element] if prop.upper is None or prop.upper > 1 else element)
        except Exception:
            UmlElement._rollback(transaction)
            raise
        finally:
            _mutation.reset(token)
        self.synchronize()
        return element

    def detach(self, element):
        return self.move(element)

    def delete(self, element, *, cascade=True, on_references='detach'):
        self._member(element)
        removed = element.delete(cascade=cascade, on_references=on_references)
        self.synchronize()
        return removed

    def synchronize(self):
        """Reconcile direct legacy mutations with live identities and roots."""
        live = sorted((e for e in self.session.elements if not e.is_deleted),
                      key=lambda e: (getattr(e, '_xmi_uri', self.uri), getattr(e, '_xmi_id', ''), e.__spec__.name))
        self.ids = {key: obj for key, obj in self.ids.items() if not obj.is_deleted}
        records = {id(v): v for v in self.runtime_values if not v.is_deleted}
        for element in live:
            for record in getattr(element, '_profile_instances', ()):
                if not record.is_deleted: records[id(record)] = record
        self.runtime_values = list(records.values())
        locations = {}
        for key, obj in self.ids.items(): locations.setdefault(id(obj), key)
        for obj in live + self.runtime_values:
            key = locations.get(id(obj))
            if key is None:
                uri = getattr(obj, '_xmi_uri', None) or self.uri
                identifier = getattr(obj, '_xmi_id', None) or 'id_'+uuid4().hex
                key = uri+'#'+identifier
                if key in self.ids and self.ids[key] is not obj:
                    identifier = 'id_'+uuid4().hex
                    key = uri+'#'+identifier
                obj._xmi_uri, obj._xmi_id = uri, identifier
                self.ids[key] = obj
                locations[id(obj)] = key
        roots = {uri: [] for uri in self.resource_roots}
        roots.setdefault(self.uri, [])
        for element in live:
            if element.owner is None:
                uri = locations[id(element)].rsplit('#', 1)[0]
                roots.setdefault(uri, []).append(element)
        self.resource_roots = roots
        self.roots = roots[self.uri]
        return self

    def identity(self, element):
        element._ensure_alive()
        self.synchronize()
        return next((key for key, obj in self.ids.items() if obj is element), None)

    def export_document(self, *, scope='document', roots=None):
        """Document scope retains every live root, including detached objects.

        Reachable scope requires explicit roots and exports only their closure.
        """
        if scope not in ('document', 'reachable'): raise ValueError('Unknown export scope')
        if scope == 'document' and roots is not None: raise ValueError('Explicit roots require reachable scope')
        if scope == 'reachable' and roots is None: raise ValueError('Reachable scope requires explicit roots')
        self.synchronize()
        export = copy.copy(self)
        export.roots = [root for group in self.resource_roots.values() for root in group] if scope == 'document' else list(roots)
        for root in export.roots: self._member(root)
        return export

    def dumps(self, *, scope='document', roots=None, **options):
        from .xmi import dumps
        return dumps(self, scope=scope, roots=roots, **options)

    def save(self, path, *, scope='document', roots=None, **options):
        from .xmi import dump
        return dump(self, path, scope=scope, roots=roots, **options)

    def validation_report(self):
        from .validation import validate_document
        self.synchronize()
        return validate_document(self)
