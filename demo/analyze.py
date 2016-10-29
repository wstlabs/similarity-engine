import sys, argparse, os
from collections import Counter
import simeng
from simeng.extras import rankmap, find_best
from simeng.util.statistics import valhist
from simeng import ioutil


parser = argparse.ArgumentParser()
parser.add_argument("--infile", type=str, required=True, help="input file")
parser.add_argument("--outdir", type=str, required=False, help="output directory")
parser.add_argument("--limit", type=int, required=False, help="dump limit")
parser.add_argument("--rename", required=False, action="store_true", help="rename users")
args = parser.parse_args()

outdir = args.outdir
if outdir is not None:
    if not os.path.exists(outdir):
        os.mkdir(outdir)


likes = ioutil.slurp_csv(args.infile,types=(str,int))
print("that be %d likes." % len(likes))

eng = simeng.ingest(likes)
eng.build()
stats = eng.stats()
for k in sorted(stats.keys()):
    print("stats[%s] = %s" % (k,stats[k]))

if args.rename:
    _rankmap = rankmap(eng)
    _rankinv = {v:k for k,v in _rankmap.items()}
    renamed = ((_rankmap[user],item) for user,item in likes)

    outfile = "%s/rankmap.json" % outdir
    print("rankmap to '%s' .." % outfile)
    ioutil.save_json(outfile,_rankmap)

    outfile = "%s/rankinv.json" % outdir
    print("rankmap to '%s' .." % outfile)
    ioutil.save_json(outfile,_rankinv)

    outfile = "%s/renamed.csv" % outdir
    print("renamed likes to '%s' .." % outfile)
    ioutil.save_csv(outfile,renamed,header=('user','item'))
    print("done.")
    sys.exit(1)

# Note that we flip (u,v) in the call to eng.overlap() to exercise the
# reflexive lookup feature.
histo = Counter(len(eng.overlap(v,u)) for u,v in eng.pairs())
print("histo with %d keys." % len(histo))
valhist = sorted(histo.items(),reverse=True)
print(valhist[0:10])

if outdir:
    header = ('value','count')
    outfile = "%s/overlap_valhist.csv" % outdir
    print("save to '%s' .." % outfile)
    ioutil.save_csv(outfile,valhist,header=header)

itemhist = Counter(eng.itemhist().values())
itemhist = sorted(itemhist.items(),reverse=True)
print("itemhist = ",itemhist[0:5])
if outdir:
    outfile = "%s/itemhist.csv" % outdir
    print("save to '%s' .." % outfile)
    ioutil.save_csv(outfile,itemhist,header=header)

N = 500
print("top %d..." % N)
pairs = sorted(((v,k) for k,v in eng.itemhist().items()),reverse=True)[0:N]
print(pairs[0:10])
if outdir:
    header = ('item_id','count')
    flipped = ((k,v) for v,k in pairs)
    outfile = "%s/top-%d.csv" % (outdir,N)
    print("save to '%s' .." % outfile)
    ioutil.save_csv(outfile,flipped,header=header)

def jaccard_histogram(eng,N):
    jhist = [0 for _ in range (0,N)]
    for u,v in eng.pairs():
        jval = eng.jaccard(u,v) * N
        k = int(jval) if jval < N else N-1
        jhist[k] += 1
    return jhist

print("jhist ..")
jhist = jaccard_histogram(eng,100)
print(jhist)



def present(x):
    if isinstance(x,float):
        return "%.5f" % x
    else:
        return x

from itertools import chain
def display(r):
    for user,summ in r.items():
        nicetups = ((user,present(value)) for user,value in summ['select'])
        nicevals = chain(*nicetups)
        yield [user,summ['likes'],summ['neighbors']] + list(nicevals) 

print("best...")
for mode in ('overlap','jaccard','surprise','logsurp'):
    r = find_best(eng,mode=mode)
    outfile = "%s/display-%s.csv" % (outdir,mode)
    print("display to %s .." % outfile)
    ioutil.save_csv(outfile,display(r),header=('user','likes','nabes','jaccard'))



print("export jaccard...")
measures = list((eng.expected_jaccard(u,v),eng.jaccard(u,v)) for u,v in eng.pairs())
print("that be %d measures." % len(measures))
print(measures[0:10])
overlap_measures = list(filter(lambda p:p[1]>0.0,measures))
print("of these, %d have overlap." % len(overlap_measures))
if outdir:
    header = ('expected','observed')
    outfile = "%s/jaccard.csv" % outdir
    print("save to '%s' .." % outfile)
    ioutil.save_csv(outfile,overlap_measures,header=header)

# Let's count the number of pairs that have observed jaccard measure greater than the 
# expectated measure.  Note that among overlapping measures this will be tilted to the 
# "above expected" measure set, simply due to the fact that we've already excluded 
# the non-overlapping pairs.  Among all pairs, it tilts in the other direction.
count_non_overlap = len(measures) - len(overlap_measures)
exp_pos = sum(1 for _ in filter(lambda p:p[1]>p[0],overlap_measures))
exp_neg = sum(1 for _ in filter(lambda p:p[1]<p[0],overlap_measures))
print("Among overlapping pairs : %d pairs below expected measure, and %d above." % (exp_neg,exp_pos)) 
print("Among all pairs         : %d pairs below expected measure, and %d above." % (count_non_overlap+exp_neg,exp_pos)) 

import statistics
print("finally...")
pairwise = (eng.surprise(u,v) for u,v in eng.pairs())
s = sorted(_ for _ in pairwise if _ > 0)
smedian = statistics.median(s)
print("surprise: count = %d, min = %4f, max = %.4f, median = %.4f" % (len(s),s[0],s[-1],smedian))
count = 20
print("surprise: top %d = %s" % (count,s[:-count:-1]))




print("all done.")
