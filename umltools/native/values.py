"""Native value queries and multiplicity bounds; infinity represents UML '*'."""
from . import query, invariant, kind


@query('ValueSpecification.booleanValue', 'ValueSpecification.integerValue',
       'ValueSpecification.realValue', 'ValueSpecification.stringValue', 'ValueSpecification.unlimitedValue')
def undefined_value(self): return None


@query('ValueSpecification.isComputable', 'ValueSpecification.isNull')
def not_computable(self): return False


@query('LiteralBoolean.isComputable', 'LiteralInteger.isComputable', 'LiteralReal.isComputable',
       'LiteralString.isComputable', 'LiteralUnlimitedNatural.isComputable', 'LiteralNull.isComputable', 'LiteralNull.isNull')
def computable(self): return True


@query('LiteralBoolean.booleanValue', 'LiteralInteger.integerValue', 'LiteralReal.realValue',
       'LiteralString.stringValue', 'LiteralUnlimitedNatural.unlimitedValue')
def literal_value(self): return self.value


@query('ValueSpecification.isCompatibleWith')
def compatible_value(self, p):
    if not isinstance(self, type(p)): return False
    if kind(self, p, 'TypedElement'):
        if self.type is None: raise ValueError('Typed value has no type')
        return self.type.conformsTo(p.type)
    return True


@query('MultiplicityElement.lowerBound')
def lower_bound(self):
    value = None if self.lowerValue is None else self.lowerValue.integerValue()
    return 1 if value is None else value


@query('ExtensionEnd.lowerBound')
def extension_lower_bound(self): return 0 if self.lowerValue is None else self.lowerValue.integerValue()


@query('MultiplicityElement.upperBound')
def upper_bound(self):
    value = None if self.upperValue is None else self.upperValue.unlimitedValue()
    return 1 if value is None else value


@query('MultiplicityElement.lower')
def lower(self): return self.lowerBound()


@query('MultiplicityElement.upper')
def upper(self): return upper_bound(self)


@query('MultiplicityElement.isMultivalued')
def multivalued(self):
    upper = upper_bound(self)
    if upper is None: raise ValueError('Undefined upper bound')
    return upper > 1


@query('MultiplicityElement.is')
def exact_bounds(self, lowerbound, upperbound): return self.lowerBound() == lowerbound and upper_bound(self) == upperbound


@query('MultiplicityElement.compatibleWith')
def compatible(self, other):
    return other.lowerBound() <= self.lowerBound() and upper_bound(self) <= upper_bound(other)


@query('MultiplicityElement.includesMultiplicity')
def includes(self, M):
    bounds = self.lowerBound(), upper_bound(self), M.lowerBound(), upper_bound(M)
    if any(value is None for value in bounds): raise ValueError('Undefined multiplicity bound')
    lower, upper, other_lower, other_upper = bounds
    return lower <= other_lower and upper >= other_upper


@invariant('MultiplicityElement.upper_ge_lower')
def upper_ge_lower(self): return upper_bound(self) >= self.lowerBound()


@invariant('MultiplicityElement.lower_ge_0')
def lower_ge_zero(self): return self.lowerBound() >= 0


@invariant('MultiplicityElement.lower_is_integer')
def integer_lower(self): return self.lowerValue is None or self.lowerValue.integerValue() is not None


@invariant('MultiplicityElement.upper_is_unlimitedNatural')
def natural_upper(self): return self.upperValue is None or self.upperValue.unlimitedValue() is not None


@invariant('ExtensionEnd.multiplicity')
def extension_multiplicity(self): return self.lowerBound() in (0, 1) and self.upperBound() == 1


@invariant('ExtensionEnd.aggregation')
def extension_aggregation(self): return self.aggregation.value == 'composite'
