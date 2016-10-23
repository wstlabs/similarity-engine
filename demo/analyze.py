import sys, argparse, time, os
from collections import Counter
import simeng
from simeng.extras import makereport
from simeng.statistics import valhist
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


rows = ioutil.slurp_csv(args.infile,types=(str,int))
print("that be %d rows." % len(rows))
for r in rows[0:3]:
    print(r)

print("now ..")
eng = simeng.ingest(rows)
print(eng.stats())

t0 = time.time()
eng.build()
dt = time.time() - t0
print("built in %.3lf sec." % dt)
print(eng.stats())

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

print("itemhist =",type(eng.itemhist()))
itemhist = Counter(eng.itemhist().values())
print("itemhist =",type(itemhist))
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
    header = ('song_id','count')
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

print("and...")
r = makereport(eng,rename=args.rename)
print(r['summary'][0:5])
t = r['table']
users = sorted(t.keys())[0:10]
for u in users:
    print("%s: %s" % (u,t[u]))

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





print("all done.")
