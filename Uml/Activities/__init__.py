"""UML 2.5.1 Activities package."""
from importlib import import_module

__all__ = ['Activity', 'ActivityEdge', 'ActivityFinalNode', 'ActivityGroup', 'ActivityNode', 'ActivityParameterNode', 'ActivityPartition', 'CentralBufferNode', 'ControlFlow', 'ControlNode', 'DataStoreNode', 'DecisionNode', 'ExceptionHandler', 'ExecutableNode', 'FinalNode', 'FlowFinalNode', 'ForkNode', 'InitialNode', 'InterruptibleActivityRegion', 'JoinNode', 'MergeNode', 'ObjectFlow', 'ObjectNode', 'Variable', 'ObjectNodeOrderingKind']

def __getattr__(name):
    if name not in __all__: raise AttributeError(name)
    value = getattr(import_module("._" + name, __name__), name)
    globals()[name] = value
    return value
