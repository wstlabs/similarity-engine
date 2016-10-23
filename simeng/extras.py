import math
from collections import OrderedDict

def active_users(eng,reverse=True):
    """Given a SimilarityEngine instance :eng, returns a list of users sorted by like activity
    (the number of like per user), in descending or ascending order, respectivtly, according
    to the True/False status of the :reverse flag, which defaults to True (for descending order).

    Strictly speaking it sorts on the tuple (like-activity,username) to  guarantee reproducibility."""
    return sorted(eng.users(),key=lambda u:(len(eng.lookup(u)),u),reverse=reverse)

def makereport(eng,rename=True):
    users = active_users(eng)
    summary = [
        {
            'user':u,
            'likes':len(eng.lookup(u)),
            'neighbors':len(eng.neighbors(u)),
        } for u in users
    ]
    t = {}
    for r in summary: 
        user = r['user']
        neighbors = sorted(eng.neighbors(user),key=lambda v:eng.jaccard(user,v),reverse=True)
        jaccard = OrderedDict((v,eng.jaccard(user,v)) for v in neighbors)
        t[user] = list(jaccard.items())[0:10]
    return {
        'summary':summary,
        'table':t
    }


def _fakename(n,k):
    if k != 2:
        raise ValueError("invalid depth")
    if n < 0 or n >= 26*26:
        raise ValueError("invalid user index")
    x,y = n//26,n%26
    return chr(ord('A')+x)+chr(ord('A')+y)

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


