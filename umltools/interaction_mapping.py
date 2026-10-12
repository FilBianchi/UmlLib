"""Explicit semantic mappings for facts absent from the core UML metamodel.

These annotations do not invent UML attributes and are scoped to the relevant
Message or PartDecomposition. All mapped objects are rechecked during validation.
"""


def _require_kind(obj, name):
    if not hasattr(obj, '__registry__') or not isinstance(obj, obj.__registry__[name]):
        raise TypeError(f'Expected a UML {name}')
    obj._ensure_alive()


def bind_gate_endpoint(message, gate, endpoint):
    _require_kind(message, 'Message')
    _require_kind(gate, 'Gate')
    _require_kind(endpoint, 'NamedElement')
    if gate not in (message.sendEvent, message.receiveEvent):
        raise ValueError('The gate must be an end of this message')
    message._gate_endpoint_bindings = {**getattr(message, '_gate_endpoint_bindings', {}), gate: endpoint}


def mark_extra_global(decomposition, fragment, *, is_extra_global=True):
    _require_kind(decomposition, 'PartDecomposition')
    _require_kind(fragment, 'CombinedFragment')
    if type(is_extra_global) is not bool: raise TypeError('is_extra_global must be Boolean')
    decomposition._extra_global_fragments = {**getattr(decomposition, '_extra_global_fragments', {}), fragment: is_extra_global}


def map_occurrence_gate(decomposition, occurrence, actual_gate, *, internal_occurrence=None):
    _require_kind(decomposition, 'PartDecomposition')
    _require_kind(occurrence, 'OccurrenceSpecification')
    _require_kind(actual_gate, 'Gate')
    if actual_gate not in decomposition.actualGate:
        raise ValueError('The actual gate must belong to this PartDecomposition')
    if internal_occurrence is not None: _require_kind(internal_occurrence, 'OccurrenceSpecification')
    decomposition._occurrence_gate_mappings = {
        **getattr(decomposition, '_occurrence_gate_mappings', {}),
        occurrence: (actual_gate, internal_occurrence),
    }
