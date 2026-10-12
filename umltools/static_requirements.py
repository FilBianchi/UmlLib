"""Supplemental static prose checks; XMI predicates remain separately inspectable.

Identifiers use prose: to distinguish these requirements from declared XMI invariants.
No expression language or Behavior is executed.
"""
from .native import kind, NativeNotImplemented, unique
from .native.constraints_basic import required, enum
from .native.constraints_actions import conforms
from .native.constraints_interactions import wildcard


REQUIREMENTS = {}


def requirement(identifier, owner, source, description):
    def register(function):
        REQUIREMENTS[identifier] = dict(owner=owner, source=source, description=description, function=function)
        return function
    return register


def check_static(model, identifier):
    model._ensure_alive()
    definition = REQUIREMENTS[identifier]
    if not kind(model, model, definition['owner']): raise TypeError('Requirement applies to '+definition['owner'])
    result = definition['function'](model)
    if type(result) is not bool: raise ValueError('Static requirement did not return Boolean')
    return result


def validate_static(model):
    from . import UnsupportedSemanticsError
    model._ensure_alive()
    issues = []
    for identifier, definition in REQUIREMENTS.items():
        if not kind(model, model, definition['owner']): continue
        try:
            if not check_static(model, identifier): issues.append(('constraint', identifier))
        except (NativeNotImplemented, UnsupportedSemanticsError, RecursionError): issues.append(('unsupported constraint', identifier))
        except (ValueError, TypeError, AttributeError, IndexError): issues.append(('invalid constraint', identifier))
    return issues


def token_types(edge, upstream=True):
    types, seen = [], set()
    pending = [required(edge.source if upstream else edge.target)]
    while pending:
        node = pending.pop()
        if node in seen: continue
        seen.add(node)
        if kind(edge, node, 'ObjectNode'):
            types.append(node.type)
        elif kind(edge, node, 'ControlNode'):
            for neighbor in node.incoming if upstream else node.outgoing:
                if not kind(edge, neighbor, 'ObjectFlow'): continue
                if neighbor.transformation is not None:
                    parameters = (neighbor.transformation.outputParameters() if upstream
                                  else neighbor.transformation.inputParameters())
                    if len(parameters) != 1: raise ValueError('Intervening transformation requires one input and one output')
                    types.append(parameters[0].type)
                else: pending.append(required(neighbor.source if upstream else neighbor.target))
    if not types or any(t is None for t in types):
        raise NativeNotImplemented('Token types require represented typed ObjectNode endpoints')
    return unique(types)


def accepts(edge, parameter):
    types = token_types(edge)
    return all(conforms(t, parameter.type) for t in types)


@requirement('prose:ObjectFlow.selection_types', 'ObjectFlow', 'ObjectFlow-input_and_output_parameter',
             'Selection inputs accept source tokens; selection outputs conform to the source type.')
def selection_types(flow):
    if flow.selection is None: return True
    inputs, outputs = flow.selection.inputParameters(), flow.selection.outputParameters()
    if len(inputs) != 1 or len(outputs) != 1: return False
    types = token_types(flow)
    return all(conforms(t, inputs[0].type) and conforms(outputs[0].type, t) for t in types)


@requirement('prose:ObjectFlow.transformation_types', 'ObjectFlow', 'ObjectFlow-transformation_behavior',
             'Transformation inputs accept upstream tokens; outputs conform to downstream types.')
def transformation_types(flow):
    if flow.transformation is None: return True
    inputs, outputs = flow.transformation.inputParameters(), flow.transformation.outputParameters()
    if len(inputs) != 1 or len(outputs) != 1: return False
    upstream, downstream = token_types(flow), token_types(flow, False)
    return all(conforms(t, inputs[0].type) for t in upstream) and all(conforms(outputs[0].type, t) for t in downstream)


@requirement('prose:DecisionNode.input_types', 'DecisionNode', 'DecisionNode-two_input_parameters',
             'Decision inputs correspond to regular tokens first and decisionInputFlow tokens second, or accept the regular object flows through one parameter.')
def decision_types(node):
    if node.decisionInput is None: return True
    parameters = node.decisionInput.inputParameters()
    decision = node.decisionInputFlow
    regular = [e for e in node.incoming if e is not decision]
    if decision is not None:
        if decision not in node.incoming or not kind(node, decision, 'ObjectFlow'): return False
        if len(regular) != 1: return False
        if kind(node, regular[0], 'ControlFlow'):
            return len(parameters) == 1 and accepts(decision, parameters[0])
        return (len(parameters) == 2 and kind(node, regular[0], 'ObjectFlow')
                and accepts(regular[0], parameters[0]) and accepts(decision, parameters[1]))
    if not regular: return False
    if any(kind(node, e, 'ControlFlow') for e in regular):
        return not parameters and all(kind(node, e, 'ControlFlow') for e in regular)
    return len(parameters) == 1 and all(kind(node, e, 'ObjectFlow') and accepts(e, parameters[0]) for e in regular)


@requirement('prose:Message.reply_argument_types', 'Message', 'Message-signature_is_operation_reply',
             'Reply values or expression first operands conform to out/inout/return parameter types; wildcards are accepted.')
def reply_types(message):
    if enum(message.messageSort) != 'reply' or not kind(message, message.signature, 'Operation'): return True
    parameters = message.signature.outputParameters()
    if len(parameters) != len(message.argument): return False
    for value, parameter in zip(message.argument, parameters):
        if wildcard(value): continue
        actual = value.operand[0] if kind(message, value, 'Expression') and value.operand else value
        if not conforms(actual.type, parameter.type): return False
    return True


def deployed_elements(target):
    """Resolve direct manifestations of Artifact objects and their modeled instances.

    This is an additive interpretation, not the Artifact-only XMI derivation.
    Multiple Artifact classifiers contribute a union. Nested artifacts, actual runtime
    copies, and slot-based redefinition of manifestations are not inferred.
    """
    target._ensure_alive()
    if not kind(target, target, 'DeploymentTarget'): raise TypeError('Expected DeploymentTarget')
    result = []
    for deployment in target.deployment:
        for value in deployment.deployedArtifact:
            if kind(target, value, 'Artifact'): artifacts = [value]
            elif kind(target, value, 'InstanceSpecification'):
                artifacts = [c for c in value.classifier if kind(target, c, 'Artifact')]
                if not artifacts: raise ValueError('Deployed instance has no Artifact classifier')
            else: raise ValueError('Unsupported DeployedArtifact kind')
            for artifact in artifacts:
                result.extend(required(m.utilizedElement) for m in artifact.manifestation)
    return unique(result)


@requirement('prose:DeploymentSpecification.configured_instance_elements', 'DeploymentSpecification',
             'DeploymentSpecification-deployed_elements', 'Configured deployments, including Artifact instances, manifest Components.')
def configured_elements(specification):
    if specification.deployment is None: return True
    target = required(specification.deployment.location)
    return all(kind(specification, e, 'Component') for e in deployed_elements(target))


SUPPLEMENTAL_QUERIES = {
    'prose:DeploymentTarget.resolved_elements': dict(owner='DeploymentTarget', source='DeploymentTarget-deployedElement',
        description='Resolve direct manifestations of Artifact objects and modeled Artifact instances.', function=deployed_elements),
}
REQUIREMENTS['prose:DecisionNode.input_types']['additional_sources'] = (
    'DecisionNode-incoming_control_one_input_parameter', 'DecisionNode-incoming_object_one_input_parameter')
