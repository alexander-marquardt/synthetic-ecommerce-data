import sys, collections
from synthetic_industrial_products.catalog import generate
from synthetic_industrial_products.catalog.config import GeneratorConfig
lines = int(sys.argv[1]) if len(sys.argv) > 1 else 2600
cat = generate.generate(GeneratorConfig().with_(lines=lines))
title = collections.defaultdict(set); bs = collections.defaultdict(set); pid = collections.Counter(); sku = collections.Counter(); img=collections.Counter()
for l in cat.lines:
    title[l.title].add(l.type_key); bs[(l.brand, l.series)].add(l.type_key); pid[l.product_id]+=1
    for c in l.children: sku[c.sku]+=1
print("lines", len(cat.lines), "skus", sum(sku.values()))
print("dup product_id", [k for k,v in pid.items() if v>1][:5], "dup sku", [k for k,v in sku.items() if v>1][:5])
print("sku lengths", collections.Counter(len(s) for s in sku), "nondigit", sum(not s.isdigit() for s in sku))
dt = {k:v for k,v in title.items() if sum(1 for l in cat.lines if l.title==k)>1} if lines<=2600 else None
c = collections.Counter(l.title for l in cat.lines)
dups = [(t, sorted(title[t]), n) for t, n in c.items() if n > 1]
print("dup product titles", len(dups), "cross-type", sum(len(x[1])>1 for x in dups)); print(dups[:6])
xbs = [(k, sorted(v)) for k, v in bs.items() if len(v) > 1]
print("(brand,series) shared across types", len(xbs), xbs[:6])
per = collections.Counter()
for l in cat.lines: per[l.type_key]+=len(l.children)
print("max skus per type", per.most_common(2))
