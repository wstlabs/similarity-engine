"""
Flips an overlap-based like table to a normalized one.
"""

import sys, argparse
import simplejson as json
import simeng.ioutil as ioutil
from collections import OrderedDict

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--infile", type=str, required=True, help="inputfile")
    parser.add_argument("--outfile", type=str, required=False, help="output file")
    return parser.parse_args()

def sort_tups(seq):
    """Nicely sorts a list of symbolic tuples, in a way we'll describe later."""
    return sorted(seq,key=lambda k:(-len(k),k),reverse=True)[::-1]

def strict_dict(pairs):
    """Creates a dict from a sequence of key-value pairs, verifying uniqueness of each key."""
    d = {}
    for k,v in pairs:
        if k in d:
            raise ValueError("duplicate tupkey '%s'" % k)
        d[k] = v
    return d

def canon_order(pairs):
    d = strict_dict(pairs)
    return [(k,d[k]) for k in sort_tups(d.keys())]

def convert(pairs):
    """Takes a sorted list of (tupkey,count) pairs, and emits a corresponding 
    sequence of (sym,item) pairs."""
    i = 1
    for tupkey,count in pairs:
        for _ in range(count):
            for sym in tupkey:
                yield sym,i
            i += 1


def run():
    args = parse_args()
    print("args = %s" % args)

    pairs = ioutil.slurp_csv(args.infile,types=(str,int))
    print("that be %d pairs." % len(pairs))
    pairs = canon_order(pairs)
    print(pairs)
    likes = convert(pairs)
    likes = list(likes)
    maxitem = likes[-1][1]
    print("that be %d likes; maxitem = %d" % (len(likes),maxitem))
    if args.outfile:
        print("save to '%s' .." % args.outfile)
        ioutil.save_csv(args.outfile,likes,header=('user','item'))
    print("done.")

if __name__ == '__main__':
    run()

