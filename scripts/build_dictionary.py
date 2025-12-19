import json
from collections import defaultdict
from pathlib import Path

INDEX_PATH = "data/processed/index.json"
BLOCK_PATH = "data/processed/blocks.json"
FRONT_PATH = "data/processed/frontcoded_blocks.json"

def build_blocks(terms, prefix_len=3):
    blocks = defaultdict(list)
    for term in sorted(terms):
        key = term[:prefix_len]
        blocks[key].append(term)
    return blocks

def front_coding(terms):
    if not terms:
        return ""

    prefix = terms[0]
    for term in terms[1:]:
        i = 0
        while i < min(len(prefix), len(term)) and prefix[i] == term[i]:
            i += 1
        prefix = prefix[:i]

    encoded = prefix + "*"
    encoded += "|".join(t[len(prefix):] for t in terms)
    return encoded

if __name__ == "__main__":
    with open(INDEX_PATH, "r") as f:
        index_data = json.load(f)

    terms = list(index_data["index"].keys())
    blocks = build_blocks(terms)

    frontcoded = {
        k: front_coding(v)
        for k, v in blocks.items()
    }

    with open(BLOCK_PATH, "w") as f:
        json.dump(blocks, f, indent=2)

    with open(FRONT_PATH, "w") as f:
        json.dump(frontcoded, f, indent=2)

    print("[OK] Blocking & Front Coding built")
