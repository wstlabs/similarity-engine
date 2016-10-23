"""
Flips an overlap-based like table to a normalized one.
"""

import sys, argparse
import simplejson as json
import ioany

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--infile", type=str, required=True, help="inputfile")
    parser.add_argument("--outfile", type=str, required=False, help="output file")
    return parser.parse_args()

def run():
    args = parse_args()
    print("args = %s" % args)

    recs = ioany.read_csv(args.infile,types=(str,int)).recs()
    d = {r['keytup']:r['count'] for r in recs}
    print(d)

if __name__ == '__main__':
    run()

