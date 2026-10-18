import sys, subprocess
sys.path.insert(0, 'scripts')
import ci_select, ci_shards
tree = ci_select.Tree(); print("tree", len(tree.py))
w = ci_shards.load_weights()
alltests = sorted(p for p in tree.py if ci_select.is_test_file(p))
tot = sum(w.get(f, 20) for f in alltests)
n = int(sys.argv[1])
commits = subprocess.check_output(["git", "rev-list", "--first-parent", "-n", str(n), "HEAD"], text=True).split()
for c in commits:
    ch, mod = ci_select.changed_paths(c + "^", c)
    chosen, why = ci_select.select(ch, tree, modified=mod)
    wt = sum(w.get(f, 20) for f in chosen)
    subj = subprocess.check_output(["git", "log", "-1", "--format=%s", c], text=True)[:60]
    print(f"{c[:8]} files={len(ch):3d} sel={len(chosen):3d}/{len(alltests)} weight={wt:6.0f}/{tot:.0f} {wt/tot:4.0%} {subj.strip()}")
