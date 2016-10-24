import time
from collections import OrderedDict, defaultdict
from itertools import combinations
from copy import deepcopy

class SimilarityEngine(object):

    def __init__(self,pairs):
        self._itemhist = None
        self._lookup = None
        self._overlap = None
        self._jaccard = None
        self._neighbors = None
        self._count = None
        self._stats = None
        self.ingest(pairs)

    def ingest(self,pairs):
        self._lookup = OrderedDict()
        self._itemhist = defaultdict(int)
        self._count = defaultdict(int)
        for user,item in pairs:
            if user not in self._lookup:
                self._lookup[user] = set()
            self._lookup[user].add(item)
            self._itemhist[item] += 1
            self._count['likes_total'] += 1

    def users(self):
        return self._lookup.keys()

    def pairs(self):
        yield from combinations(self.users(),2)

    def build(self):
        t0 = time.time()
        self.build_overlap()
        self.build_jaccard()
        self.build_counts()
        delta = time.time() - t0
        self._stats = {'delta':delta}

    def build_overlap(self):
        self._overlap = {}
        self._neighbors = defaultdict(set)
        for u,v in combinations(self.users(),2):
            common = self._lookup[u].intersection(self._lookup[v])
            self._overlap[(u,v)] = common
            if len(common):
                self._neighbors[u].add(v)
                self._neighbors[v].add(u)

    def build_jaccard(self):
        self._jaccard = {}
        for u,v in combinations(self.users(),2):
            common = self.overlap(u,v)
            union  = self._lookup[u].union(self._lookup[v])
            if len(union):
                self._jaccard[(u,v)] = len(common) / len(union)
            else:
                self._jaccard[(u,v)] = None

    def build_counts(self):
        self._count['likes_min'] = min(len(self._lookup[u]) for u in self.users())
        self._count['likes_max'] = max(len(self._lookup[u]) for u in self.users())

    def lookup(self,u):
        return self._lookup.get(u)

    def overlap(self,u,v):
        if self._overlap is None:
            raise RuntimeError("invalid operation - overlaps not initialized")
        return looksym(self._overlap,u,v)

    def jaccard(self,u,v):
        if self._jaccard is None:
            raise RuntimeError("invalid operation - jaccard measure not initialized")
        return looksym(self._jaccard,u,v)

    def expected_jaccard(self,u,v):
        """Expected jaccard measure of two samples of the same sizes as the actual likes for users :u and :v, 
           respectively, (naively) assuming a uniform distrbution over our total space of :items."""
        prob_u = len(self._lookup[u]) / len(self._itemhist)
        prob_v = len(self._lookup[v]) / len(self._itemhist)
        return prob_u * prob_v / (prob_u + prob_v - prob_u * prob_v)

    def surprise(self,u,v):
        jaccard = self.jaccard(u,v)
        return None if jaccard is None else jaccard / self.expected_jaccard(u,v)

    def neighbors(self,u):
        if self._neighbors is None:
            raise RuntimeError("invalid operation - neighbor lookups not initialized")
        if u in self._neighbors:
            return deepcopy(self._neighbors[u])
        # If you're not in the neighbors lookup, it's possible that you're a valid user
        # but had no overlaps with our neighbors. 
        if u in self._lookup:
            return set()
        else:
            raise KeyError("invalid user '%s'" % u)

    def itemhist(self):
        """Returns a dict representing the number of users who have liked each item."""
        return deepcopy(self._itemhist)

    @property
    def counts(self):
        return dict(self._count)

    def stats(self):
        general = {
            'users': len(self._lookup),
            'items': len(self._itemhist),
            'overlaps': None if self._overlap is None else len(self._overlap)//2,
        }
        return {
           'general': general,
           'count': self.counts,
           'build': deepcopy(self._stats),
        }


def looksym(d,a,b):
    '''Performs a symmetric lookup on a dict :d'''
    if (a,b) in d:
        return d[(a,b)]
    if (b,a) in d:
        return d[(b,a)]
    raise KeyError("invalid tuple (%s,%s)" % (a,b))

def ingest(pairs):
    return SimilarityEngine(pairs)


