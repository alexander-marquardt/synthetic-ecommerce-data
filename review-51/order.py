import random, hashlib, json
from synthetic_industrial_products.catalog import generate, emit
from synthetic_industrial_products.catalog.config import GeneratorConfig
from synthetic_industrial_products.catalog.model import Catalog
cfg = GeneratorConfig()
def dump(lines): return hashlib.sha256("".join(json.dumps(d, sort_keys=True) for d in emit.iter_nested(Catalog(lines=tuple(lines)))).encode()).hexdigest()[:16]
whole = generate.generate(cfg).lines
keys = generate.all_type_keys(); sh = keys[:]; random.Random(3).shuffle(sh)
# build types in a shuffled order (separate Generator per type), then join in key order
parts = {k: generate.generate_type(cfg, k) for k in sh}
print("shuffled-build joined in key order == whole:", dump(whole) == dump([l for k in keys for l in parts[k]]))
print("generate(types=shuffled) == whole:", dump(generate.generate(cfg, types=sh).lines) == dump(whole))
# golden file matches
g = open('golden-catalog/nested.jsonl').read().splitlines()
print("committed golden == fresh:", [json.loads(x) for x in g] == list(emit.iter_nested(Catalog(lines=whole))))
