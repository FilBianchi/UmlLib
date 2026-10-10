"""Message ends and gates. Source errata are documented in SPECIFICATION_NOTES."""
from . import query, kind, unique, reverse, single


def combined_fragment(self):
    return single(reverse(self, 'CombinedFragment', 'cfragmentGate'))


def operand_fragment(operand):
    return None if operand is None else single(reverse(operand, 'CombinedFragment', 'operand'))


def message(self):
    if self.message is None: raise ValueError('MessageEnd query requires a message')
    return self.message


@query('MessageEnd.oppositeEnd')
def opposite(self):
    m = message(self)
    return unique(e for e in (m.sendEvent, m.receiveEvent) if e is not None and e is not self)


@query('MessageEnd.isSend')
def is_send(self): return message(self).sendEvent is self


@query('MessageEnd.isReceive')
def is_receive(self): return message(self).receiveEvent is self


@query('Message.messageKind')
def message_kind(self):
    name = 'complete' if self.sendEvent is not None and self.receiveEvent is not None else 'lost' if self.sendEvent is not None else 'found' if self.receiveEvent is not None else 'unknown'
    return self.__registry__['MessageKind'][name]


@query('Message.isDistinguishableFrom', 'Gate.isDistinguishableFrom')
def distinguishable(self, n, ns): return True


def surrounding(fragment):
    if fragment is None: return []
    return unique(e for e in (fragment.enclosingInteraction, fragment.enclosingOperand) if e is not None)


def other_fragment(self):
    ends = self.oppositeEnd()
    if not ends: return None
    other = ends[0]
    return combined_fragment(other) if kind(self, other, 'Gate') else other


@query('Gate.isOutsideCF')
def outside(self):
    fragment = combined_fragment(self)
    if fragment is None: return False
    other = other_fragment(self)
    return other is not None and bool(surrounding(fragment)) and set(surrounding(fragment)) == set(surrounding(other))


@query('Gate.isInsideCF')
def inside(self):
    fragment = combined_fragment(self)
    if fragment is None: return False
    other = other_fragment(self)
    operand = None if other is None else other.enclosingOperand
    return operand is not None and operand_fragment(operand) is fragment


@query('Gate.isActual')
def actual(self): return bool(reverse(self, 'InteractionUse', 'actualGate'))


@query('Gate.isFormal')
def formal(self): return bool(reverse(self, 'Interaction', 'formalGate'))


@query('Gate.getName')
def gate_name(self):
    if self.name is not None: return self.name
    m = message(self)
    if m.name is None: raise ValueError('An unnamed gate requires a named message')
    outgoing = self.isSend() == (self.isActual() or self.isOutsideCF())
    return ('out_' if outgoing else 'in_') + m.name


@query('Gate.matches')
def matches(self, gateToMatch):
    a, b = message(self), message(gateToMatch)
    return (self.getName() == gateToMatch.getName() and a.messageSort == b.messageSort and a.name == b.name and a.signature is b.signature and (not self.isSend() or gateToMatch.isReceive()) and (not self.isReceive() or gateToMatch.isSend()))


@query('Gate.getOperand')
def operand(self):
    return other_fragment(self).enclosingOperand if self.isInsideCF() else None


@query('MessageEnd.enclosingFragment')
def enclosing(self):
    if kind(self, self, 'Gate'):
        if self.isOutsideCF(): return surrounding(combined_fragment(self))
        if self.isInsideCF(): return [combined_fragment(self)]
        if self.isFormal(): return reverse(self, 'Interaction', 'formalGate')
        if self.isActual(): return surrounding(single(reverse(self, 'InteractionUse', 'actualGate')))
        return []
    return surrounding(self)
