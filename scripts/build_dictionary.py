import json
from collections import defaultdict
from pathlib import Path

INDEX_PATH = Path("data/processed/index.json")
BLOCK_PATH = Path("data/processed/blocks.json")
FRONT_PATH = Path("data/processed/frontcoded.json")

def front_code(terms):
    if not terms:
        return ""
    prefix = terms[0]
    for term in terms[1:]:
        i = 0
        while i < min(len(prefix), len(term)) and prefix[i] == term[i]:
            i += 1
        prefix = prefix[:i]
    return prefix + "*" + "|".join(t[len(prefix):] for t in terms)

with open(INDEX_PATH) as f:
    index = json.load(f)["index"]

terms = sorted(index.keys())
blocks = defaultdict(list)

for term in terms:
    blocks[term[:3]].append(term)

frontcoded = {k: front_code(v) for k, v in blocks.items()}

json.dump(blocks, open(BLOCK_PATH, "w"), indent=2)
json.dump(frontcoded, open(FRONT_PATH, "w"), indent=2)

print("[OK] Blocking & front coding built")
