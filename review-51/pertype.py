"""Dump a sha per type of the nested docs, for the given config tweak (argv[1] json)."""
import hashlib, json, sys, time
from synthetic_industrial_products.catalog import emit, generate
from synthetic_industrial_products.catalog.config import GeneratorConfig
from synthetic_industrial_products.catalog.model import Catalog
tweak = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
cfg = GeneratorConfig()
for k, v in tweak.items():
    if k == "type_weights_reorder":
        cfg = cfg.with_(type_weights=dict(reversed(list(cfg.type_weights.items()))), new_type_share=dict(reversed(list(cfg.new_type_share.items()))))
    elif k in ("type_weights", "new_type_share"):
        d = dict(getattr(cfg, k)); d.update(v); cfg = cfg.with_(**{k: d})
    else:
        cfg = cfg.with_(**{k: v})
t = time.time()
cat = generate.generate(cfg)
out = {}
for line in cat.lines:
    h = out.setdefault(line.type_key, hashlib.sha256())
    for d in emit.iter_nested(Catalog(lines=(line,)), emit.DEFAULT_IMAGE_BASE_URL):
        h.update(json.dumps(d, sort_keys=True).encode())
    for d in emit.iter_flat(Catalog(lines=(line,)), emit.DEFAULT_IMAGE_BASE_URL):
        h.update(json.dumps(d, sort_keys=True).encode())
whole = hashlib.sha256("".join(l.product_id for l in cat.lines).encode()).hexdigest()[:12]
json.dump({"whole_order": whole, "n": len(cat.lines), "types": {k: h.hexdigest()[:16] for k, h in sorted(out.items())}}, sys.stdout)
print(f"\n{time.time()-t:.1f}s", file=sys.stderr)
