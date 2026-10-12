from collections.abc import MutableSequence


class UmlCollection(MutableSequence):
    """Mutations pass through the property's model-level checks."""
    def __init__(self, owner, name, values=()):
        self.owner, self.name, self._data = owner, name, list(values)

    def __len__(self):
        self.owner._ensure_alive()
        return len(self._data)
    def __getitem__(self, index):
        self.owner._ensure_alive()
        return self._data[index]

    def __setitem__(self, index, value):
        values = list(self._data)
        values[index] = value
        setattr(self.owner, self.name, values)

    def __delitem__(self, index):
        values = list(self._data)
        del values[index]
        setattr(self.owner, self.name, values)

    def insert(self, index, value):
        values = list(self._data)
        values.insert(index, value)
        setattr(self.owner, self.name, values)

    def extend(self, values):
        setattr(self.owner, self.name, list(self._data) + list(values))

    def reverse(self):
        setattr(self.owner, self.name, list(reversed(self._data)))

    def sort(self, *, key=None, reverse=False):
        setattr(self.owner, self.name, sorted(self._data, key=key, reverse=reverse))

    def __repr__(self): return repr(self._data)
    def __eq__(self, other): return self._data == list(other) if isinstance(other, (list, tuple, UmlCollection)) else False
