"""Small, interpreted OCL expression engine; never executes Python source.

Unsupported syntax and operations raise OclUnsupported instead of passing a rule.
This engine is a subset of OCL, not a complete implementation of its type system.
"""
import re
import itertools
from enum import Enum
from collections.abc import Sequence
from .collections import UmlCollection


class OclUnsupported(NotImplementedError):
    pass


TOKEN = re.compile(r"\s*(--[^\n]*|'(?:''|[^'])*'|\d+(?:\.\d+)?|[A-Za-z_]\w*|->|::|<>|<=|>=|[().,;|{}:+*/=<>-])")
PRECEDENCE = {'implies': 1, 'or': 2, 'xor': 2, 'and': 3, '=': 4, '<>': 4, '<': 4, '>': 4, '<=': 4, '>=': 4, '+': 5, '-': 5, '*': 6, '/': 6, 'div': 6, 'mod': 6}


class Parser:
    def __init__(self, source):
        self.tokens = []
        position = 0
        while position < len(source.rstrip()):
            match = TOKEN.match(source, position)
            if not match:
                raise OclUnsupported(f'Unsupported syntax at {source[position:position+30]!r}')
            if not match[1].startswith('--'):
                self.tokens.append(match[1])
            position = match.end()
        self.tokens.append('<end>')
        self.index = 0

    def peek(self):
        return self.tokens[self.index]

    def take(self, expected=None):
        token = self.peek()
        if expected is not None and token != expected:
            raise OclUnsupported(f'Expected {expected}, found {token}')
        self.index += 1
        return token

    def type_annotation(self):
        self.take(':')
        self.take()
        if self.peek() == '(':
            self.take()
            depth = 1
            while depth:
                token = self.take()
                if token == '<end>': raise OclUnsupported('Unterminated type annotation')
                depth += (token == '(') - (token == ')')

    def expr(self, minimum=0):
        token = self.take()
        if token in ('not', '-'):
            node = ('unary', token, self.expr(7))
        elif token == '(':
            node = self.expr()
            self.take(')')
        elif token == 'if':
            condition = self.expr()
            self.take('then')
            yes = self.expr()
            self.take('else')
            no = self.expr()
            self.take('endif')
            node = ('if', condition, yes, no)
        elif token == 'let':
            bindings = []
            while True:
                variable = self.take()
                if self.peek() == ':': self.type_annotation()
                self.take('=')
                bindings.append((variable, self.expr()))
                if self.peek() != ',': break
                self.take()
            self.take('in')
            node = self.expr()
            for variable, value in reversed(bindings): node = ('let', variable, value, node)
        elif token.startswith("'"):
            node = ('literal', token[1:-1].replace("''", "'"))
        elif token[0].isdigit():
            node = ('literal', float(token) if '.' in token else int(token))
        elif token == 'invalid':
            node = ('invalid',)
        elif token == '*':
            node = ('literal', float('inf'))
        elif token in ('true', 'false', 'null'):
            node = ('literal', {'true': True, 'false': False, 'null': None}[token])
        elif re.fullmatch(r'[A-Za-z_]\w*', token):
            node = ('name', token)
        else:
            raise OclUnsupported(f'Unexpected token: {token}')
        while True:
            token = self.peek()
            if token in ('.', '->', '::'):
                self.take()
                node = ('get', node, self.take(), token)
            elif token == '{' and node[0] == 'name' and node[1] in ('Set', 'Sequence', 'OrderedSet', 'Bag'):
                self.take()
                items = []
                if self.peek() != '}':
                    items.append(self.expr())
                    while self.peek() == ',':
                        self.take()
                        items.append(self.expr())
                self.take('}')
                node = ('collection', node[1], items)
            elif token == '(':
                self.take()
                args = []
                if self.peek() != ')':
                    # A comma introduces multiple iterator variables only when
                    # a pipe occurs before the next closing parenthesis.
                    ahead = self.tokens[self.index:]
                    multi = self.tokens[self.index+1] == ',' and '|' in ahead and ahead.index('|') < ahead.index(')')
                    if self.tokens[self.index+1] in ('|', ':') or multi:
                        variable = self.take()
                        variables = [variable]
                        if self.peek() == ':': self.type_annotation()
                        while self.peek() == ',':
                            self.take()
                            variables.append(self.take())
                            if self.peek() == ':': self.type_annotation()
                        if self.peek() == ';':
                            self.take()
                            accumulator = self.take()
                            if self.peek() == ':': self.type_annotation()
                            self.take('=')
                            initial = self.expr()
                            self.take('|')
                            args = [('iterate', variable, accumulator, initial, self.expr())]
                        else:
                            self.take('|')
                            args = [('lambda', variables, self.expr())]
                    else:
                        args.append(self.expr())
                        while self.peek() == ',':
                            self.take()
                            args.append(self.expr())
                self.take(')')
                node = ('call', node, args)
            elif token in PRECEDENCE and PRECEDENCE[token] >= minimum:
                self.take()
                node = ('binary', token, node, self.expr(PRECEDENCE[token] + (0 if token == 'implies' else 1)))
            else:
                break
        return node


def unique(values):
    result = []
    for value in values:
        if value not in result:
            result.append(value)
    return result


class OclCollection(list):
    def __init__(self, values=(), kind='Set'):
        self.kind = kind
        super().__init__(unique(values) if kind in ('Set', 'OrderedSet') else values)


def collection(value):
    if isinstance(value, OclCollection): return value
    if isinstance(value, UmlCollection):
        flags = value.owner.properties()[value.name].flags
        kind = ('OrderedSet' if flags.get('isUnique', 'true') == 'true' else 'Sequence') if flags.get('isOrdered') == 'true' else ('Set' if flags.get('isUnique', 'true') == 'true' else 'Bag')
        return OclCollection(value, kind)
    return OclCollection([] if value is None else list(value) if isinstance(value, Sequence) and not isinstance(value, str) else [value])


def call(receiver, name, args, env):
    if name.startswith('_'): raise OclUnsupported('Private Python names are not OCL features')
    if name == 'allInstances':
        if not isinstance(receiver, type) or not hasattr(receiver, '__instances__'): raise OclUnsupported('allInstances requires a UML classifier')
        return OclCollection([obj for obj in receiver.__instances__ if isinstance(obj, receiver) and obj.__registry__ is env['_registry']])
    values = collection(receiver)
    if name == 'iterate':
        _, variable, accumulator, initial, body = args[0]
        result = run(initial, env)
        for value in values:
            result = run(body, {**env, variable: value, accumulator: result})
        return result
    if name in ('forAll', 'exists', 'select', 'reject', 'collect', 'collectNested', 'one', 'isUnique', 'any', 'sortedBy', 'closure'):
        if args[0][0] == 'lambda':
            variables, body = args[0][1:]
            if len(variables) > 1 and name not in ('forAll', 'exists'): raise OclUnsupported('Multiple variables only supported for forAll/exists')
            results = [run(body, {**env, **dict(zip(variables, row))}) for row in itertools.product(values, repeat=len(variables))]
        else:
            results = [run(args[0], {**env, 'self': value}) for value in values]
        if name == 'sortedBy': return OclCollection([v for _, v in sorted(zip(results, values), key=lambda pair: pair[0])], 'OrderedSet' if values.kind in ('Set', 'OrderedSet') else 'Sequence')
        if name == 'closure':
            result, pending = [], list(values)
            while pending:
                current = pending.pop(0)
                if current in result: continue
                result.append(current)
                if args[0][0] == 'lambda':
                    if len(variables) != 1: raise OclUnsupported('closure requires one iterator variable')
                    next_values = run(body, {**env, variables[0]: current})
                else: next_values = run(args[0], {**env, 'self': current})
                pending.extend(collection(next_values))
            return OclCollection(result)
        if name in ('forAll', 'exists', 'one', 'any', 'select', 'reject') and any(r is not None and type(r) is not bool for r in results): raise ValueError('Iterator requires Boolean expression')
        if name == 'forAll': return False if False in results else None if None in results else True
        if name == 'exists': return True if True in results else None if None in results else False
        if name in ('one', 'any', 'select', 'reject') and None in results: raise ValueError('Undefined iterator predicate')
        if name == 'one': return sum(results) == 1
        if name == 'isUnique': return len(unique(results)) == len(results)
        if name == 'any': return next((v for v, r in zip(values, results) if r), None)
        if name == 'select': return OclCollection([v for v, r in zip(values, results) if r], values.kind)
        if name == 'reject': return OclCollection([v for v, r in zip(values, results) if not r], values.kind)
        kind = 'Sequence' if values.kind in ('Sequence', 'OrderedSet') else 'Bag'
        if name == 'collectNested': return OclCollection(results, kind)
        return OclCollection([item for result in results for item in collection(result)], kind)
    arguments = [run(arg, env) for arg in args]
    if name == 'oclIsUndefined': return receiver is None
    if name == 'oclIsKindOf': return isinstance(receiver, arguments[0])
    if name == 'oclIsTypeOf': return type(receiver) is arguments[0]
    if name == 'oclAsType':
        if not isinstance(receiver, arguments[0]): raise ValueError('Invalid OCL cast')
        return receiver
    if name == 'size': return len(receiver) if isinstance(receiver, str) else len(values)
    if name == 'isEmpty': return not values
    if name == 'notEmpty': return bool(values)
    if name in ('asSet', 'asOrderedSet', 'asSequence', 'asBag'): return OclCollection(values, name[2:])
    if name == 'includes': return arguments[0] in values
    if name == 'excludes': return arguments[0] not in values
    if name == 'includesAll': return all(x in values for x in collection(arguments[0]))
    if name == 'excludesAll': return all(x not in values for x in collection(arguments[0]))
    if name == 'union':
        other = collection(arguments[0])
        if values.kind not in ('Set', 'Bag') or other.kind not in ('Set', 'Bag'): raise OclUnsupported('union requires Set or Bag')
        return OclCollection(values + other, 'Bag' if 'Bag' in (values.kind, other.kind) else 'Set')
    if name == 'intersection':
        other = list(collection(arguments[0]))
        result = []
        for value in values:
            if value in other:
                result.append(value)
                other.remove(value)
        return OclCollection(result, values.kind)
    if name == 'including': return OclCollection(values + arguments, values.kind)
    if name == 'excluding': return OclCollection([v for v in values if v != arguments[0]], values.kind)
    if name == 'first': return values[0]
    if name == 'last': return values[-1]
    if name == 'at': return values[arguments[0]-1]
    if name == 'sum': return sum(values)
    if name == 'count': return values.count(arguments[0])
    if name == 'indexOf': return values.index(arguments[0]) + 1
    if name == 'reverse': return OclCollection(reversed(values), values.kind)
    if name == 'append': return OclCollection(values + arguments, values.kind)
    if name == 'prepend': return OclCollection(arguments + values, values.kind)
    if name in ('subSequence', 'subOrderedSet'): return OclCollection(values[arguments[0]-1:arguments[1]], values.kind)
    if name == 'flatten':
        def flatten(items):
            return [x for item in items for x in (flatten(item) if isinstance(item, Sequence) and not isinstance(item, str) else [item])]
        return OclCollection(flatten(values), values.kind)
    if name == 'concat': return receiver + arguments[0]
    if name == 'substring': return receiver[arguments[0]-1:arguments[1]]
    if name == 'toUpper': return receiver.upper()
    if name == 'toLower': return receiver.lower()
    if name == 'abs': return abs(receiver)
    if name == 'max': return max(receiver, arguments[0])
    if name == 'min': return min(receiver, arguments[0])
    if hasattr(receiver, 'properties') and name in receiver.properties():
        from .semantics import operation
        for base in type(receiver).__mro__:
            spec = base.__dict__.get('__spec__')
            if spec and name in spec.operations:
                return operation(receiver, spec.name, name, arguments)
    if hasattr(receiver, 'properties'):
        allowed = any(name in base.__dict__['__spec__'].operations for base in type(receiver).__mro__ if '__spec__' in base.__dict__)
        if allowed:
            method = getattr(receiver, name, None)
            if callable(method): return method(*arguments)
    raise OclUnsupported(f'Unsupported operation: {name}')


def run(node, env):
    kind = node[0]
    if kind == 'literal': return node[1]
    if kind == 'invalid': raise ValueError('OCL invalid')
    if kind == 'let': return run(node[3], {**env, node[1]: run(node[2], env)})
    if kind == 'collection':
        values = [run(item, env) for item in node[2]]
        return OclCollection(values, node[1])
    if kind == 'name':
        if node[1].startswith('_'): raise OclUnsupported('Private Python names are not OCL features')
        if node[1] in env: return env[node[1]]
        if node[1] in env['_registry']: return env['_registry'][node[1]]
        return getattr(env['self'], node[1])
    if kind == 'get':
        receiver = run(node[1], env)
        name = node[2]
        if name.startswith('_'): raise OclUnsupported('Private Python names are not OCL features')
        if isinstance(receiver, Sequence) and not isinstance(receiver, str): return [item for v in receiver for item in collection(getattr(v, name))]
        if isinstance(receiver, type) and issubclass(receiver, Enum): return receiver(name)
        return getattr(receiver, name)
    if kind == 'call':
        target = node[1]
        if target[0] == 'get':
            receiver = run(target[1], env)
            if target[3] == '.' and isinstance(receiver, Sequence) and not isinstance(receiver, str):
                return [item for value in receiver for item in collection(call(value, target[2], node[2], env))]
            return call(receiver, target[2], node[2], env)
        if target[0] == 'name': return call(env['self'], target[1], node[2], env)
        raise OclUnsupported('Unsupported call target')
    if kind == 'if':
        condition = run(node[1], env)
        if type(condition) is not bool: raise ValueError('if requires a defined Boolean condition')
        return run(node[2] if condition else node[3], env)
    if kind == 'unary':
        value = run(node[2], env)
        if node[1] == 'not' and value is not None and type(value) is not bool: raise ValueError('not requires Boolean')
        return (None if value is None else not value) if node[1] == 'not' else -value
    if kind == 'binary':
        operator = node[1]
        left = run(node[2], env)
        if operator == 'and' and left is False: return False
        if operator == 'or' and left is True: return True
        if operator == 'implies' and left is False: return True
        right = run(node[3], env)
        if operator in ('and', 'or', 'implies', 'xor'):
            if left is not None and type(left) is not bool or right is not None and type(right) is not bool:
                raise ValueError('Boolean operands required')
            if operator == 'and': return False if left is False or right is False else None if left is None or right is None else True
            if operator == 'or': return True if left is True or right is True else None if left is None or right is None else False
            if operator == 'implies': return True if left is False or right is True else None if left is None or right is None else False
            return None if left is None or right is None else left != right
        if operator == '=': return left == right
        if operator == '<>': return left != right
        if operator == '<': return left < right
        if operator == '>': return left > right
        if operator == '<=': return left <= right
        if operator == '>=': return left >= right
        if operator == '+': return left + right
        if operator == '-': return left - right
        if operator == '*': return left * right
        if operator == '/': return left / right
        if operator == 'div': return left // right
        if operator == 'mod': return left % right
    raise OclUnsupported(f'Unsupported expression: {kind}')


def evaluate(source, self, **variables):
    parser = Parser(source)
    tree = parser.expr()
    if parser.peek() != '<end>':
        raise OclUnsupported(f'Unconsumed syntax: {parser.peek()}')
    return run(tree, {'self': self, '_registry': self.__registry__, **variables})
