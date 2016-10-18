from collections import defaultdict

def valhist(pairs):
    h = defaultdict(int)
    for item,value in pairs:
        h[value] += 1
    return h

