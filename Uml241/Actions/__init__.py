"""UML 2.4.1 Actions package."""
from importlib import import_module

__all__ = ['AcceptCallAction', 'AcceptEventAction', 'Action', 'ActionInputPin', 'AddStructuralFeatureValueAction', 'AddVariableValueAction', 'BroadcastSignalAction', 'CallAction', 'CallBehaviorAction', 'CallOperationAction', 'Clause', 'ClearAssociationAction', 'ClearStructuralFeatureAction', 'ClearVariableAction', 'ConditionalNode', 'CreateLinkAction', 'CreateLinkObjectAction', 'CreateObjectAction', 'DestroyLinkAction', 'DestroyObjectAction', 'ExpansionNode', 'ExpansionRegion', 'InputPin', 'InvocationAction', 'LinkAction', 'LinkEndCreationData', 'LinkEndData', 'LinkEndDestructionData', 'LoopNode', 'OpaqueAction', 'OutputPin', 'Pin', 'QualifierValue', 'RaiseExceptionAction', 'ReadExtentAction', 'ReadIsClassifiedObjectAction', 'ReadLinkAction', 'ReadLinkObjectEndAction', 'ReadLinkObjectEndQualifierAction', 'ReadSelfAction', 'ReadStructuralFeatureAction', 'ReadVariableAction', 'ReclassifyObjectAction', 'ReduceAction', 'RemoveStructuralFeatureValueAction', 'RemoveVariableValueAction', 'ReplyAction', 'SendObjectAction', 'SendSignalAction', 'SequenceNode', 'StartClassifierBehaviorAction', 'StartObjectBehaviorAction', 'StructuralFeatureAction', 'StructuredActivityNode', 'TestIdentityAction', 'UnmarshallAction', 'ValuePin', 'ValueSpecificationAction', 'VariableAction', 'WriteLinkAction', 'WriteStructuralFeatureAction', 'WriteVariableAction', 'ExpansionKind']

def __getattr__(name):
    if name not in __all__: raise AttributeError(name)
    value = getattr(import_module("._" + name, __name__), name)
    globals()[name] = value
    return value
