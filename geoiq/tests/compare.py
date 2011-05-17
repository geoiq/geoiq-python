
import difflib, sys
__all__ = [ "DeepCompare" ]

class DeepIter(object):
    def run(self, sub):
        if (hasattr(sub, "iteritems")): return self.run_dict(sub)
        elif (hasattr(sub, "__iter__")): return self.run_iter(sub)
        else: return [sub].__iter__()
    
    def run_dict(self, x):
        yield "__dict"
        itms = sorted(x.iteritems())
        for (k,v) in itms: 
            for subitm in self.run(v):
                yield(k,subitm)
        yield "__end_dict"

    def run_iter(self, x):
        yield "__subiter"
        for i in x: 
            for subitm in self.run(i):
                yield subitm
        yield "__end_subiter"

class DeepCompare(object):
    def __init__(self):
        self.matcher = difflib.SequenceMatcher(self.is_junk)

    def compare(self, a, b):
        sa,sb = (list(s) for s in self.get_iters(a,b))
        self.matcher.set_seqs(sa,sb)
        
        results = list(self.matcher.get_matching_blocks())
        
        rlen = sum( n for (i,j,n) in results )
        match = len(sa) == rlen and len(sb) == rlen
        
        
        def map_matches(rs):
            a_idx = 0
            b_idx = 0
            for (i,j,l) in rs:
                a_diff = i - a_idx
                b_diff = j - b_idx
                diff_a = sa[a_idx:a_idx+a_diff]
                diff_b = sb[b_idx:b_idx+b_diff]

                diffs = [ (x,y) for (x,y,z) in zip(diff_b,diff_a,range(max(a_diff,b_diff))) ]
                yield {
                    "diff" : diffs
                    }
                yield {
                    "same" : sa[i:i+l]
                    }
                a_idx = i + l
                b_idx = j + l
        return (match, list(map_matches(results)))

    def pprint(self,resmap, outp, full_ok=True):
        def green(x):
            return ("\033[92m%s\033[0m" % x)
        def red(x):
            return ("\033[91m%s\033[0m" % x)

        for r in resmap:
            if ("same" in r):
                if not full_ok:
                    outp.write("%s %d\n" % (green("same : "), len(r["same"])))
                    continue
                for v in r["same"]:
                    outp.write("%s %s\n" % (green("same : "), repr(v)))
            else:
                for va,vb in r["diff"]:
                    outp.write("%s %s -- %s\n" % (red("diff : "), repr(va),repr(vb)))


    def get_iters(self, a, b):
        return (DeepIter().run(a), DeepIter().run(b))

    def is_junk(self, value):
        return False
    
