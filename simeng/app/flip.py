"""
Flips an overlap-based like table to a normalized one.
"""

import sys, argparse
import simplejson as json
import ioany
from collections import OrderedDict

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--infile", type=str, required=True, help="inputfile")
    parser.add_argument("--outfile", type=str, required=False, help="output file")
    return parser.parse_args()

def sort_tups(seq):
    """Nicely sorts a list of symbolic tuples, in a way we'll describe later."""
    return sorted(seq,key=lambda k:(-len(k),k),reverse=True)[::-1]

def run():
    args = parse_args()
    print("args = %s" % args)

    recs = ioany.read_csv(args.infile,types=(str,int)).recs()
    d = {r['keytup']:r['count'] for r in recs}
    print(d)
    tups = sort_tups(d.keys())
    print(tups)
    pairs = [(k,d[k]) for k in tups]
    print(pairs)

if __name__ == '__main__':
    run()

