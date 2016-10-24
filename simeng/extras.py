import math
from collections import OrderedDict

def active_users(engine,reverse=True):
    """Given a SimilarityEngine instance :eng, returns a list of users sorted by like activity
    (the number of like per user), in descending or ascending order, respectivtly, according
    to the True/False status of the :reverse flag, which defaults to True (for descending order).

    Strictly speaking it sorts on the tuple (like-activity,username) to  guarantee reproducibility."""
    return sorted(engine.users(),key=lambda u:(len(engine.lookup(u)),u),reverse=reverse)

def select_jaccard(engine,user,count):
    neighbors = sorted(engine.neighbors(user),key=lambda v:engine.jaccard(user,v),reverse=True)
    jaccard = OrderedDict((v,engine.jaccard(user,v)) for v in neighbors)
    return list(jaccard.items())[:count]

def project(engine,user):
    return {
        'likes':len(engine.lookup(user)),
        'neighbors':len(engine.neighbors(user)),
        'jaccard':select_jaccard(engine,user,10)
    }

def find_best(engine):
    users = active_users(engine)
    return OrderedDict((user,project(engine,user)) for user in users)

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


