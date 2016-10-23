from collections import OrderedDict

def makereport(eng,rename=True):
    users = sorted(eng.users(),key=lambda u:len(eng.lookup(u)),reverse=True)
    summary = [
        {
            'user':u,
            'likes':len(eng.lookup(u)),
            'neighbors':len(eng.neighbors(u)),
        } for u in users
    ]
    t = {}
    for i,r in enumerate(summary):
        user = r['user']
        name = fakename(i,2) if rename else user
        neighbors = sorted(eng.neighbors(user),key=lambda v:eng.jaccard(user,v),reverse=True)
        jaccard = OrderedDict((v,eng.jaccard(user,v)) for v in neighbors)
        t[name] = list(jaccard.items())[0:10]
    return {
        'summary':summary,
        'table':t
    }


def fakename(n,k):
    if k != 2:
        raise ValueError("invalid depth")
    if n < 0 or n >= 26*26:
        raise ValueError("invalid user index")
    x,y = n//26,n%26
    return chr(ord('A')+x)+chr(ord('A')+y)

