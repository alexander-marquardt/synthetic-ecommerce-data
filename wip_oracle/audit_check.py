import json, sys
sys.path.insert(0, 'scripts')
import ci_select
tree = ci_select.Tree()
bad = 0
n = 0
for line in open('.agent/audit.jsonl'):
    r = json.loads(line)
    for t in r['tests']:
        n += 1
        for f in sorted(set(r['imported']) | set(r['opened'])):
            if f == t or not (f in tree.files):
                continue
            if f.startswith(('.venv', '.agent')):
                continue
            if not tree.reaches(t, f) and f != t:
                bad += 1
                print("MISSED", t, f)
print("tests checked", n, "missed", bad)
