"""Copyright (c) 2012 Nezar Abdennur

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import sys
from collections import Mapping, MutableMapping
class _AbstractEntry(object):
    __slots__ = ('dkey', 'pkey')
    def __init__(self, dkey, pkey):
        self.dkey = dkey
        self.pkey = pkey
    def __lt__(self, other):
        raise NotImplementedError
    def __repr__(self):
        return self.__class__.__name__ + \
            "(%s: %s)" % (repr(self.dkey), self.pkey)
class _MinEntry(_AbstractEntry):
    __slots__ = ()
    __init__ = _AbstractEntry.__init__
    def __eq__(self, other):
        return self.pkey == other.pkey
    def __lt__(self, other):
        return self.pkey < other.pkey
class _MaxEntry(_AbstractEntry):
    __slots__ = ()
    __init__ = _AbstractEntry.__init__
    def __eq__(self, other):
        return self.pkey == other.pkey
    def __lt__(self, other):
        return self.pkey > other.pkey
def new_entry_class(comparator):
    class _CustomEntry(_AbstractEntry):
        __lt__ = comparator
    return _CustomEntry
class PQDict(MutableMapping):
    _entry_class = _MinEntry
    __eq__ = MutableMapping.__eq__
    __ne__ = MutableMapping.__ne__
    keys = MutableMapping.keys
    values = prioritykeys = MutableMapping.values
    items = MutableMapping.items
    get = MutableMapping.get
    clear = MutableMapping.clear
    update = MutableMapping.update
    setdefault = MutableMapping.setdefault
    def __init__(self, *args, **kwargs):
        if len(args) > 1:
            raise TypeError('Too many arguments')
        self._heap = []
        self._position = {}
        pos = 0
        if args:
            if isinstance(args[0], Mapping) or hasattr(args[0], 'items'):
                seq = args[0].items()
            else:
                seq = args[0]
            for dkey, pkey in seq:
                entry = self._entry_class(dkey, pkey)
                self._heap.append(entry)
                self._position[dkey] = pos
                pos += 1
        if kwargs:
            for dkey, pkey in kwargs.items():
                entry = self._entry_class(dkey, pkey)
                self._heap.append(entry)
                self._position[dkey] = pos
                pos += 1
        self._heapify()
    @classmethod
    def minpq(cls, *args, **kwargs):
        pq = cls()
        pq._entry_class = _MinEntry
        pq.__init__(*args, **kwargs)
        return pq
    @classmethod
    def maxpq(cls, *args, **kwargs):
        pq = cls()
        pq._entry_class = _MaxEntry
        pq.__init__(*args, **kwargs)
        return pq
    @classmethod
    def fromkeys(cls, iterable, value=None, rank_by=None, maxpq=False):
        if value and rank_by:
            raise TypeError("Received both 'value' and 'rank_by' argument.")
        if value is None:
            value = float('-inf') if maxpq else float('inf')
        if maxpq:
            cls = cls.maxpq
        if rank_by is None:
            return cls( (dkey, value) for dkey in iterable )
        else:
            return cls( (dkey, rank_by(dkey)) for dkey in iterable )
    @classmethod
    def create(cls, prio):
        pq = cls()
        if isinstance(prio, PQDict):
            pq._entry_class = prio._entry_class
        else:
            pq._entry_class = new_entry_class(prio)
        return pq
    @property
    def pq_type(self):
        if self._entry_class == _MinEntry:
            return 'min'
        elif self._entry_class == _MaxEntry:
            return 'max'
        else:
            return 'custom'
    def __len__(self):
        return len(self._heap)
    def __contains__(self, dkey):
        return dkey in self._position
    def __iter__(self):
        for entry in self._heap:
            yield entry.dkey
    def __getitem__(self, dkey):
        return self._heap[self._position[dkey]].pkey
    def __setitem__(self, dkey, pkey):
        heap = self._heap
        position = self._position
        try:
            pos = position[dkey]
        except KeyError:
            n = len(self._heap)
            self._heap.append(self._entry_class(dkey, pkey))
            self._position[dkey] = n
            self._swim(n)
        else:
            heap[pos].pkey = pkey
            parent_pos = (pos - 1) >> 1
            child_pos = 2*pos + 1
            if parent_pos > -1 and heap[pos] < heap[parent_pos]:
                self._swim(pos)
            elif child_pos < len(heap):
                other_pos = child_pos + 1
                if (other_pos < len(heap) 
                        and not heap[child_pos] < heap[other_pos]):
                    child_pos = other_pos
                if heap[child_pos] < heap[pos]:
                    self._sink(pos)
    def __delitem__(self, dkey):
        heap = self._heap
        position = self._position
        pos = position.pop(dkey)
        entry_to_delete = heap[pos]
        end = heap.pop(-1)
        if end is not entry_to_delete:
            heap[pos] = end
            position[end.dkey] = pos
            parent_pos = (pos - 1) >> 1
            child_pos = 2*pos + 1
            if parent_pos > -1 and heap[pos] < heap[parent_pos]:
                self._swim(pos)
            elif child_pos < len(heap):
                other_pos = child_pos + 1
                if (other_pos < len(heap) and
                        not heap[child_pos] < heap[other_pos]):
                    child_pos = other_pos
                if heap[child_pos] < heap[pos]:
                    self._sink(pos)
        del entry_to_delete
    def __copy__(self):
        from copy import copy
        other = self.__class__()
        other._heap = [copy(entry) for entry in self._heap]
        other._position = copy(self._position)
        return other
    copy = __copy__
    def __repr__(self):
        things = ', '.join(['%s: %s' % (repr(entry.dkey), entry.pkey) 
                                for entry in self._heap])
        return self.__class__.__name__ + '({' + things  + '})'
    __marker = object()
    def pop(self, dkey=__marker, default=__marker):
        heap = self._heap
        position = self._position
        if dkey is self.__marker:
            if not heap:
                raise KeyError('PQDict is empty')
            dkey = heap[0].dkey
            del self[dkey]
            return dkey
        try:
            pos = position.pop(dkey)
        except KeyError:
            if default is self.__marker:
                raise
            return default
        else:
            entry_to_delete = heap[pos]
            pkey = entry_to_delete.pkey
            end = heap.pop(-1)
            if end is not entry_to_delete:
                heap[pos] = end
                position[end.dkey] = pos
                parent_pos = (pos - 1) >> 1
                child_pos = 2*pos + 1
                if parent_pos > -1 and heap[pos] < heap[parent_pos]:
                    self._swim(pos)
                elif child_pos < len(heap):
                    other_pos = child_pos + 1
                    if (other_pos < len(heap) 
                            and not heap[child_pos] < heap[other_pos]):
                        child_pos = other_pos
                    if heap[child_pos] < heap[pos]:
                        self._sink(pos)
            del entry_to_delete
            return pkey
    def popitem(self):
        heap = self._heap
        position = self._position
        try:
            end = heap.pop(-1)
        except IndexError:
            raise KeyError('PQDict is empty')
        if heap:
            entry = heap[0]
            heap[0] = end
            position[end.dkey] = 0
            self._sink(0)
        else:
            entry = end
        del position[entry.dkey]
        return entry.dkey, entry.pkey
    def _heapify(self):
        n = len(self._heap)
        for pos in reversed(range(n//2)):
            self._sink(pos)
    def _sink(self, top=0):
        heap = self._heap
        position = self._position
        endpos = len(heap)
        pos = top
        entry = heap[pos]
        child_pos = 2*pos + 1
        while child_pos < endpos:
            other_pos = child_pos + 1
            if other_pos < endpos and not heap[child_pos] < heap[other_pos]:
                child_pos = other_pos
            child_entry = heap[child_pos]
            heap[pos] = child_entry
            position[child_entry.dkey] = pos
            pos = child_pos
            child_pos = 2*pos + 1
        heap[pos] = entry
        position[entry.dkey] = pos
        self._swim(pos, top)
    def _swim(self, pos, top=0):
        heap = self._heap
        position = self._position
        entry = heap[pos]
        while pos > top:
            parent_pos = (pos - 1) >> 1
            parent_entry = heap[parent_pos]
            if entry < parent_entry:
                heap[pos] = parent_entry
                position[parent_entry.dkey] = pos
                pos = parent_pos
                continue
            break
        heap[pos] = entry
        position[entry.dkey] = pos

def dijkstra(G, start, end=None):
    inf = float('inf')
    D = {start: 0}
    Q = PQDict(D)
    P = {}
    U = set(G.keys())
    while U:
        (v, d) = Q.popitem()
        D[v] = d
        U.remove(v)
        if v == end: break
        for w in G[v]:
            if w in U:
                d = D[v] + G[v][w]
                if d < Q.get(w, inf):
                    Q[w] = d
                    P[w] = v
    return D, P

def shortest_path(G, start, end):
    dist, pred = dijkstra(G, start, end)
    v = end
    path = [v]
    while v != start:
        v = pred[v]
        path.append(v)        
    path.reverse()
    return path

def test_shortest_path():
    graph = {'a': {'b': 1}, 
             'b': {'c': 2, 'b': 5}, 
             'c': {'d': 1},
             'd': {}}
    print('-- graph A --')
    x, y = 'a', 'a'
    print("{} to {}: path: {}".format(x, y, shortest_path(graph, x, y)))
    x, y = 'a', 'b'
    print("{} to {}: path: {}".format(x, y, shortest_path(graph, x, y)))
    x, y = 'a', 'c'
    print("{} to {}: path: {}".format(x, y, shortest_path(graph, x, y)))
    x, y = 'a', 'd'
    print("{} to {}: path: {}".format(x, y, shortest_path(graph, x, y)))
    graph = {'a': {'b':14, 'c':9, 'd':7},
             'b': {'a':14, 'c':2, 'e':9},
             'c': {'a':9, 'b':2, 'd':10, 'f':11},
             'd': {'a':7, 'c':10, 'f':15},
             'e': {'b':9, 'f':6},
             'f': {'c':11, 'd':15, 'e':6}}
    print('-- graph B --')
    x, y = 'a', 'f'
    print("{} to {}: path: {}".format(x, y, shortest_path(graph, x, y)))
    graph = {'a': {'b': 1, 'c': 1}, 
             'b': {'a': 1, 'c': 1}, 
             'c': {'a': 1, 'b': 1},}
    print('-- graph C --')
    x, y = 'a', 'b'
    print("{} to {}: path: {}".format(x, y, shortest_path(graph, x, y)))

if __name__ == '__main__':
    test_shortest_path()