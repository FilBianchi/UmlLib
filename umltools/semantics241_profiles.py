"""2.4.1 runtime base-link requirements; not extra XMI invariant declarations.

Superstructure 18.3.2/18.3.6 (printed pp.664-665, 680-684) models an
application in conjunction with one of the extended metaclasses. The three
2.5.1 base-property invariant identifiers do not exist in the old metamodel.
"""
from .native import NativeNotImplemented
from .native.constraints_remaining import base_properties


def definition_issues(stereotype):
    issues=[]
    for prop in base_properties(stereotype):
        low,high=prop.lowerBound(),prop.upperBound()
        if low is None or high is None:
            raise NativeNotImplemented('Base-link bounds require numeric evidence')
        if high!=1:issues.append('prose:Stereotype.base_link_upper_bound')
        if low not in (0,1):issues.append('prose:Stereotype.base_link_lower_bound')
    return list(dict.fromkeys(issues))
