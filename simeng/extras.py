import math
from collections import OrderedDict

def active_users(engine,reverse=True):
    """Given a SimilarityEngine instance, returns a list of users sorted by like activity
    (the number of like per user), in descending or ascending order, respectively, according
    to the True/False status of the :reverse flag, which defaults to True (for descending order).

    Strictly speaking it sorts on the tuple (like-activity,username) to guarantee reproducibility."""
    return sorted(engine.users(),key=lambda u:(len(engine.lookup(u)),u),reverse=reverse)

def findmax(engine,user,measure,depth):
    """Returns a list of top (user,measure) pairs, sorted by measure, up to a given :depth"""
    neighbors = engine.neighbors(user)
    d = {v:measure(user,v) for v in neighbors}
    ranked = sorted(neighbors,key=lambda v:d[v],reverse=True)
    return list((v,d[v]) for v in ranked[:depth])

def select_measure(engine,mode):
    """Derives a suitable pairwise measure function based on a keyword argument."""
    _measure = {
        'jaccard': lambda u,v:engine.jaccard(u,v),
        'surprise': lambda u,v:engine.surprise(u,v),
        'overlap': lambda u,v:len(engine.overlap(u,v)),
    }
    if mode not in _measure:
        raise ValueError("invalid mode '%s'" % mode)
    return _measure[mode]

def project(engine,user,mode='jaccard',depth=10):
    """Given a SimilarityEngine instance, a :user and a :mode, returns a dict with
    the following measures for that user:

    likes - total number of likes
    neighbors - total number of neighbors
    select - a list of tuples of (neighbor_id,measure) for the top matches
        according to that measure, up to the specified :depth
    """
    measure = select_measure(engine,mode)
    return {
        'likes':len(engine.lookup(user)),
        'neighbors':len(engine.neighbors(user)),
        'select':findmax(engine,user,measure,depth)
    }

def find_best(engine,mode):
    users = active_users(engine)
    return OrderedDict((user,project(engine,user,mode)) for user in users)

def assert_posint(n):
    if not (isinstance(n,int) and n >= 0):
        raise TypeError("invalid usage - need a positive integer")

def _base26(n):
    assert_posint(n)
    if n < 26:
        return chr(ord('A') + n)
    else:
        return _base26(n // 26) + _base26(n % 26)

def base26(n,k):
    return _base26(n).rjust(k,'A')


def rename_likes(d,likes):
    for user,item in likes:
        if user in d:
            yield d[user],item
        else:
            raise ValueError("invalid rename map: no lookup for user '%s'" % user)

# XXX provide description
def rankmap(engine):
    """
    Given an :engine, returns a dict providing a mapping from usernames to a special
    base-26 indecator of activity index (full description tba).
    """
    users = active_users(engine)
    n = len(users)
    k = math.ceil(math.log(n,26))
    return {user:base26(i,k) for i,user in enumerate(users)}


